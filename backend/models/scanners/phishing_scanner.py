import os
import re
import json
import math
import logging
import joblib
import numpy as np
import requests
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

try:
    import tldextract
except ImportError:
    tldextract = None

try:
    import whois
except ImportError:
    whois = None

try:
    import ssl
    import socket
except ImportError:
    ssl = None
    socket = None

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "weights")
URL_MODEL_PATH = os.path.join(MODEL_DIR, "iso_url_v1.joblib")
URL_SCALER_PATH = os.path.join(MODEL_DIR, "url_scaler_v1.joblib")

# Pretrained model path (new primary model)
PRETRAINED_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "model.pkl")

# Google Safe Browsing API
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "")
ENABLE_GOOGLE_SAFE_BROWSING = os.getenv("ENABLE_GOOGLE_SAFE_BROWSING", "true").lower() == "true"
ENABLE_DOMAIN_AGE_CHECK = os.getenv("ENABLE_DOMAIN_AGE_CHECK", "true").lower() == "true"
ENABLE_SSL_CHECK = os.getenv("ENABLE_SSL_CHECK", "true").lower() == "true"
ENABLE_PAGE_INSPECTION = os.getenv("ENABLE_PAGE_INSPECTION", "true").lower() == "true"
ENABLE_PRETRAINED_MODEL = os.getenv("ENABLE_PRETRAINED_MODEL", "true").lower() == "true"

# Allowlist/Blocklist file path
ALLOWLIST_BLOCKLIST_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "url_list.json")

# Known shorteners and suspicious keywords
SHORTENER_DOMAINS = {
    'bit.ly', 'tinyurl.com', 't.co', 'shorturl.at', 'goo.gl', 'ow.ly', 
    'is.gd', 'tiny.cc', 'ur.ly', 'surl.li', 'clck.ru', 'lnk.co'
}

SUSPICIOUS_KEYWORDS = [
    'secure', 'verify', 'login', 'pay', 'payments', 'upi', 'confirm', 
    'account', 'auth', 'password', 'reset', 'update', 'confirm-identity',
    'urgent', 'action-required', 'click-here', 'validate', 'authenticate',
    'suspended', 'locked', 'compromised', 'breach', 'fraud', 'alert'
]

TOP_TRUSTED = {
    'google.com', 'facebook.com', 'amazon.com', 'paypal.com', 'stripe.com', 
    'apple.com', 'microsoft.com', 'github.com', 'stackoverflow.com',
    'reddit.com', 'linkedin.com', 'twitter.com', 'instagram.com', 'youtube.com',
    'bank-of-america.com', 'chase.com', 'wellsfargo.com', 'bofa.com'
}

# Default blocklist for known malicious domains
DEFAULT_BLOCKLIST = {
    'malicious-domain.xyz', 'phishing-site.tk', 'fake-bank.ml', 
    'secure-paypal-verify.xyz', 'confirm-amazon-login.tk', 
    'bank-verify-account.ml', 'upi-verify-update.icu',
    'google-security-check.xyz', 'microsoft-account-verify.tk',
    'apple-id-security.ml', 'facebook-login-confirm.icu'
}

IP_REGEX = re.compile(r'(^|://)(\d+\.\d+\.\d+\.\d+)(:|/|$)')
SUSPICIOUS_TLDS = {'xyz', 'top', 'club', 'info', 'online', 'site', 'icu', 'pw', 'ml', 'tk', 'ga', 'cf', 'gq'}

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)

def has_suspicious_tld(domain: str) -> float:
    parts = domain.split('.')
    tld = parts[-1] if parts else ''
    return 1.0 if tld in SUSPICIOUS_TLDS else 0.0

# Load models
url_model = None
url_scaler = None
pretrained_model = None

# Load pretrained model first (primary model)
if ENABLE_PRETRAINED_MODEL and os.path.exists(PRETRAINED_MODEL_PATH):
    try:
        import warnings
        # Suppress scikit-learn version warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            pretrained_model = joblib.load(PRETRAINED_MODEL_PATH)
        logger.info("✓ Pretrained URL detection model loaded successfully")
    except ModuleNotFoundError as e:
        logger.warning(f"⚠ Could not load pretrained model - missing module: {e}")
        logger.info("  (This is usually due to scikit-learn version mismatch. Falling back to heuristics.)")
    except Exception as e:
        logger.warning(f"⚠ Could not load pretrained model: {e}")

# Load fallback IsolationForest model
if os.path.exists(URL_MODEL_PATH):
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            url_model = joblib.load(URL_MODEL_PATH)
            if os.path.exists(URL_SCALER_PATH):
                url_scaler = joblib.load(URL_SCALER_PATH)
        if url_model:
            logger.info("✓ URL IsolationForest model loaded successfully")
    except Exception as e:
        logger.warning(f"⚠ Could not load URL model: {e}")


# ============================================================================
# ALLOWLIST / BLOCKLIST MANAGEMENT
# ============================================================================

def load_blocklist() -> set:
    """Load custom blocklist from JSON file."""
    blocklist = DEFAULT_BLOCKLIST.copy()
    try:
        if os.path.exists(ALLOWLIST_BLOCKLIST_PATH):
            with open(ALLOWLIST_BLOCKLIST_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                blocklist.update(data.get('blocklist', []))
                logger.info(f"Loaded {len(blocklist)} blocklist entries")
    except Exception as e:
        logger.warning(f"Could not load custom blocklist: {e}")
    return blocklist


def check_blocklist(domain: str) -> Optional[Dict[str, Any]]:
    """Check domain against blocklist.
    
    Returns:
        Dict with high risk info if blocklisted
        None if domain not in blocklist
    """
    if not domain:
        return None
    
    domain_clean = domain.replace('www.', '').lower()
    blocklist = load_blocklist()
    
    for blocked in blocklist:
        if domain_clean == blocked or domain_clean.endswith('.' + blocked):
            logger.warning(f"Domain {domain} found in blocklist: {blocked}")
            return {
                "source": "blocklist",
                "reason": f"Domain is in blocklist (known malicious)",
                "score": 1.0
            }
    
    return None


# ============================================================================
# EXTERNAL API CHECKS
# ============================================================================

def check_google_safe_browsing(url: str) -> Optional[Dict[str, Any]]:
    """
    Check URL against Google Safe Browsing API.
    
    Returns: Dict with threat info or None if safe/check disabled
    """
    if not ENABLE_GOOGLE_SAFE_BROWSING or not GOOGLE_SAFE_BROWSING_API_KEY:
        return None
    
    try:
        endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}"
        
        payload = {
            "client": {
                "clientId": "hackethon-risk-scanner",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION"
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        
        response = requests.post(endpoint, json=payload, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('matches'):
                threat_types = [m.get('threatType', 'UNKNOWN') for m in data['matches']]
                logger.warning(f"Google Safe Browsing threat detected for {url}: {threat_types}")
                return {
                    "source": "google_safe_browsing",
                    "reason": f"Google Safe Browsing detected threats: {', '.join(threat_types)}",
                    "score": 0.95
                }
        elif response.status_code == 400:
            logger.debug(f"Invalid URL for Google Safe Browsing: {url}")
        
        return None
    
    except requests.exceptions.Timeout:
        logger.debug("Google Safe Browsing API timeout - skipping check")
        return None
    except requests.exceptions.ConnectionError:
        logger.debug("Google Safe Browsing API connection error - skipping check")
        return None
    except Exception as e:
        logger.warning(f"Google Safe Browsing check failed: {e}")
        return None


def check_domain_age(domain: str) -> Optional[Dict[str, Any]]:
    """Check domain age via WHOIS."""
    if not ENABLE_DOMAIN_AGE_CHECK or not whois:
        return None
    
    try:
        domain_to_check = domain.replace('www.', '').lower()
        w = whois.whois(domain_to_check)
        created_date = w.creation_date
        
        if isinstance(created_date, list):
            created_date = created_date[0] if created_date else None
        if not created_date:
            return None
        
        if isinstance(created_date, str):
            try:
                created_date = datetime.fromisoformat(created_date.split('T')[0])
            except:
                return None
        
        age_days = (datetime.now() - created_date).days
        
        if age_days < 30:
            return {"score": 0.4, "reason": f"Domain registered only {age_days} days ago (HIGH RISK)"}
        elif age_days < 180:
            return {"score": 0.15, "reason": f"Domain registered {age_days} days ago (relatively new)"}
    except Exception:
        pass
    
    return None


def check_ssl_certificate(url: str) -> Optional[Dict[str, Any]]:
    """Check SSL certificate validity and issuer reputation."""
    if not ENABLE_SSL_CHECK or not (ssl and socket):
        return None
    
    try:
        parsed = urlparse(url if url.startswith('http') else 'http://' + url)
        hostname = parsed.netloc.split(':')[0]
        if not hostname:
            return None
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                if not cert:
                    return {"score": 0.3, "reason": "No SSL certificate found"}
                
                not_after_str = cert.get('notAfter')
                if not_after_str:
                    not_after = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    if days_until_expiry < 7:
                        return {"score": 0.25, "reason": f"SSL certificate expires in {days_until_expiry} days"}
                
                issuer = dict(x[0] for x in cert.get('issuer', []))
                subject = dict(x[0] for x in cert.get('subject', []))
                if issuer == subject:
                    return {"score": 0.35, "reason": "Self-signed SSL certificate"}
    except Exception:
        pass
    
    return None


def score_with_pretrained_model(url: str) -> Optional[Dict[str, Any]]:
    """
    Score URL using the pretrained model.
    
    Returns: Dict with model_score and confidence if successful, None otherwise
    """
    if pretrained_model is None:
        return None
    
    try:
        # Extract URL features for the pretrained model
        url_lower = url.lower().strip()
        
        # Basic feature extraction
        domain_part = urlparse(url_lower if url_lower.startswith('http') else 'http://' + url_lower).netloc
        
        # Create feature vector based on common URL characteristics
        features = {
            'url_length': len(url_lower),
            'domain_length': len(domain_part),
            'num_dots': url_lower.count('.'),
            'num_hyphens': url_lower.count('-'),
            'num_slashes': url_lower.count('/'),
            'num_special_chars': sum(1 for c in url_lower if not c.isalnum() and c not in '.-_/'),
            'has_http': 1 if url_lower.startswith('http') else 0,
            'has_https': 1 if url_lower.startswith('https') else 0,
            'suspicious_keywords': sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower),
            'is_ip': 1 if IP_REGEX.search(url_lower) else 0,
            'entropy': shannon_entropy(url_lower),
        }
        
        # Prepare feature array in consistent order
        feature_array = np.array([[
            features['url_length'],
            features['domain_length'],
            features['num_dots'],
            features['num_hyphens'],
            features['num_slashes'],
            features['num_special_chars'],
            features['has_http'],
            features['has_https'],
            features['suspicious_keywords'],
            features['is_ip'],
            features['entropy']
        ]], dtype=float)
        
        # Score using pretrained model
        try:
            # Try different prediction methods
            if hasattr(pretrained_model, 'predict_proba'):
                # If it's a classifier with probability output
                proba = pretrained_model.predict_proba(feature_array)
                # Assume class 1 is malicious
                model_score = float(proba[0][1]) if proba.shape[1] > 1 else float(proba[0][0])
            elif hasattr(pretrained_model, 'predict'):
                # If it's a basic classifier
                prediction = pretrained_model.predict(feature_array)[0]
                model_score = float(prediction) if isinstance(prediction, (int, float)) else (1.0 if prediction else 0.0)
            elif hasattr(pretrained_model, 'score'):
                # If it's a regression model
                model_score = float(pretrained_model.score(feature_array))
            elif callable(pretrained_model):
                # If it's a callable object
                output = pretrained_model(feature_array)
                model_score = float(output[0][0])
            else:
                logger.warning("Pretrained model has no recognized prediction method")
                return None
            
            logger.info(f"Pretrained model score for URL: {model_score:.2f}")
            return {
                'model_score': min(1.0, max(0.0, model_score)),
                'confidence': 'high' if model_score >= 0.7 else 'medium' if model_score >= 0.4 else 'low',
                'source': 'pretrained_model'
            }
        except Exception as e:
            logger.warning(f"Error during model prediction: {e}")
            return None
    
    except Exception as e:
        logger.warning(f"Pretrained model scoring failed: {e}")
        return None


# ============================================================================
# MAIN SCANNING FUNCTION
# ============================================================================

def scan_url_heuristics(url: str) -> Dict[str, Any]:
    """
    Main URL scanning function combining all checks.
    
    Execution order:
    1. Blocklist check (high risk if matched)
    2. Google Safe Browsing API (if enabled)
    3. Heuristic checks (IP, shorteners, TLDs, etc.)
    4. Domain reputation (age, SSL)
    5. ML model scoring
    
    Returns:
        Dict with flagged, reasons, score, verdict
    """
    if not url:
        return {
            "flagged": False,
            "reasons": [],
            "score": 0.0,
            "verdict": "safe"
        }
    
    reasons = []
    score_acc = 0.0
    url_l = url.lower().strip()
    checks_run = []
    
    # Domain extraction
    domain = ""
    tld = ""
    try:
        if tldextract:
            ext = tldextract.extract(url_l)
            domain = ".".join(part for part in [ext.domain, ext.suffix] if part)
            tld = ext.suffix.lower() if ext.suffix else ""
        else:
            parsed = urlparse(url_l if url_l.startswith('http') else 'http://' + url_l)
            host = (parsed.netloc or parsed.path).lower()
            if ':' in host: 
                host = host.split(':')[0]
            domain = host
            tld = host.split('.')[-1] if '.' in host else ''
    except Exception:
        pass

    # ===== CHECK 1: BLOCKLIST =====
    checks_run.append("blocklist")
    blocklist_result = check_blocklist(domain)
    if blocklist_result:
        return {
            "flagged": True,
            "reasons": [blocklist_result['reason']],
            "score": 1.0,
            "verdict": "malicious",
            "checks_run": checks_run
        }
    
    # ===== CHECK 2: GOOGLE SAFE BROWSING API =====
    if ENABLE_GOOGLE_SAFE_BROWSING:
        checks_run.append("google_safe_browsing")
        google_result = check_google_safe_browsing(url)
        if google_result:
            return {
                "flagged": True,
                "reasons": [google_result['reason']],
                "score": google_result['score'],
                "verdict": "malicious",
                "checks_run": checks_run
            }

    # Trusted domain handling - still scan but with high bar
    is_trusted = domain in TOP_TRUSTED or any(domain.endswith('.' + t) for t in TOP_TRUSTED)

    # ===== CHECK 3: IP ADDRESS =====
    checks_run.append("ip_check")
    if IP_REGEX.search(url_l):
        reasons.append("URL uses raw IP address")
        score_acc += 0.7

    # ===== CHECK 4: SHORTENERS =====
    checks_run.append("shortener_check")
    for sdom in SHORTENER_DOMAINS:
        if sdom in domain:
            reasons.append("URL uses a known shortener (high risk for malicious content)")
            score_acc += 0.8
            break

    # ===== CHECK 5: SUSPICIOUS TLDS =====
    checks_run.append("tld_check")
    if tld in SUSPICIOUS_TLDS:
        reasons.append(f"Suspicious TLD: .{tld}")
        score_acc += 0.35

    # ===== CHECK 6: PUNYCODE =====
    checks_run.append("punycode_check")
    if 'xn--' in url_l:
        reasons.append("Punycode or IDN detected (possible spoofing)")
        score_acc += 0.6

    # ===== CHECK 7: SUSPICIOUS KEYWORDS =====
    checks_run.append("keyword_check")
    keyword_count = 0
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in url_l:
            keyword_count += 1
            reasons.append(f"Suspicious keyword '{kw}' in URL")
            score_acc += 0.25

    # ===== CHECK 8: HYPHENS =====
    checks_run.append("hyphen_check")
    hyphen_count = url_l.count('-')
    if hyphen_count > 5:
        reasons.append(f"Excessive hyphens ({hyphen_count}) suggest obfuscation")
        score_acc += 0.3
    elif hyphen_count > 3:
        reasons.append(f"Multiple hyphens ({hyphen_count}) in domain")
        score_acc += 0.2

    # ===== CHECK 9: URL LENGTH =====
    checks_run.append("length_check")
    if len(url_l) > 150:
        reasons.append("Very long URL (possible redirect/obfuscation)")
        score_acc += 0.15
    elif len(url_l) > 100:
        reasons.append("Long URL")
        score_acc += 0.08

    # ===== CHECK 10: UNENCRYPTED HTTP =====
    checks_run.append("encryption_check")
    if url_l.startswith("http://") and not url_l.startswith("http://localhost"):
        if any(kw in url_l for kw in ['pay', 'transaction', 'bank', 'upi', 'account']):
            reasons.append("Unencrypted HTTP used for payment-related domain")
            score_acc += 0.3
        else:
            reasons.append("Unencrypted HTTP (not HTTPS)")
            score_acc += 0.25

    # ===== CHECK 11: DOMAIN REPUTATION =====
    if ENABLE_DOMAIN_AGE_CHECK and domain:
        checks_run.append("domain_age_check")
        age_result = check_domain_age(domain)
        if age_result:
            reasons.append(age_result['reason'])
            score_acc += age_result['score']

    if ENABLE_SSL_CHECK and url_l.startswith('https'):
        checks_run.append("ssl_check")
        ssl_result = check_ssl_certificate(url_l)
        if ssl_result:
            reasons.append(ssl_result['reason'])
            score_acc += ssl_result['score']

    # ===== CHECK 12: PRETRAINED MODEL SCORING (PRIMARY) =====
    if ENABLE_PRETRAINED_MODEL and pretrained_model is not None:
        checks_run.append("pretrained_model")
        pretrained_result = score_with_pretrained_model(url)
        if pretrained_result:
            model_score = pretrained_result['model_score']
            # Use pretrained model score with higher weight (60% of ensemble)
            if score_acc > 0:
                # Combine with existing heuristic score
                score_acc = 0.4 * score_acc + 0.6 * model_score
            else:
                # If no heuristic signals, use model score directly
                score_acc = model_score
            
            if model_score >= 0.7:
                reasons.append("Pretrained ML model detected malicious patterns")
            elif model_score >= 0.4:
                reasons.append("Pretrained ML model detected suspicious patterns")

    # ===== CHECK 13: FALLBACK ML MODEL SCORING =====
    elif url_model is not None:
        checks_run.append("ml_model")
        try:
            host_to_feat = domain or url_l
            path_query = ""
            try:
                p = urlparse(url_l if url_l.startswith('http') else 'http://' + url_l)
                path_query = (p.path or "") + (p.query or "")
            except:
                pass
            
            tokens = re.split(r'[^a-z0-9]+', url_l)
            digit_tokens = sum(1 for t in tokens if t.isdigit())
            kw_count = sum(1 for kw in ['secure','verify','login','pay','payments','upi','confirm','account','auth'] if kw in url_l)
            
            feats = [
                len(host_to_feat), 
                host_to_feat.count('-'),
                host_to_feat.count('.'),
                digit_tokens,
                kw_count,
                shannon_entropy(host_to_feat + path_query),
                sum(1 for c in url_l if not c.isalnum()),
                has_suspicious_tld(host_to_feat),
                len(url_l)
            ]
            
            X = np.array([feats], dtype=float)
            if url_scaler is not None:
                X = url_scaler.transform(X)
            
            raw = url_model.decision_function(X)
            val = float(-raw[0])
            model_score = 1 / (1 + math.exp(-val))
            
            # Combine heuristic score with model score (50-50 ensemble)
            score_acc = 0.5 * score_acc + 0.5 * model_score
        except Exception as e:
            logger.warning(f"Model scoring failed: {e}")

    # ===== MULTI-SIGNAL DETECTION BOOST =====
    # Multiple risk signals together indicate high malicious intent
    high_risk_keywords = {
        "forms", "password", "login", "verify", "confirm", 
        "unencrypted", "shortener", "suspicious", "punycode",
        "excessive", "ip address"
    }
    malicious_signals = sum(
        1 for reason in reasons 
        if any(kw.lower() in reason.lower() for kw in high_risk_keywords)
    )
    
    if malicious_signals >= 4:
        score_acc = min(1.0, score_acc + 0.25)
    elif malicious_signals >= 3:
        score_acc = min(1.0, score_acc + 0.15)
    elif malicious_signals >= 2:
        score_acc = min(1.0, score_acc + 0.08)

    # ===== FINALIZE =====
    # Lowered threshold from 0.5 to 0.35 to catch more malicious URLs
    final_score = min(1.0, score_acc)
    flagged = final_score >= 0.35
    
    if not reasons:
        reasons.append("No clear issues detected")
    
    # Determine verdict
    if final_score >= 0.7:
        verdict = "malicious"
    elif final_score >= 0.4:
        verdict = "suspicious"
    else:
        verdict = "safe"
    
    return {
        "flagged": flagged,
        "reasons": reasons,
        "score": round(final_score, 2),
        "verdict": verdict,
        "checks_run": checks_run
    }
