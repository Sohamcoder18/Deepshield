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

# Model paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "weights")
URL_MODEL_PATH = os.path.join(MODEL_DIR, "iso_url_v1.joblib")
URL_SCALER_PATH = os.path.join(MODEL_DIR, "url_scaler_v1.joblib")

# Configuration
ENABLE_DOMAIN_AGE_CHECK = True
ENABLE_SSL_CHECK = True
ENABLE_PAGE_INSPECTION = True

# Known shorteners and suspicious keywords
SHORTENER_DOMAINS = {
    'bit.ly', 'tinyurl.com', 't.co', 'shorturl.at', 'goo.gl', 'ow.ly', 
    'is.gd', 'tiny.cc', 'ur.ly', 'surl.li', 'clck.ru', 'lnk.co'
}

SUSPICIOUS_KEYWORDS = [
    'secure', 'verify', 'login', 'pay', 'payments', 'upi', 'confirm', 
    'account', 'auth', 'password', 'reset', 'update', 'confirm-identity'
]

TOP_TRUSTED = {
    'google.com', 'facebook.com', 'amazon.com', 'paypal.com', 'stripe.com', 
    'apple.com', 'microsoft.com', 'github.com', 'stackoverflow.com',
    'reddit.com', 'linkedin.com', 'twitter.com', 'instagram.com', 'youtube.com'
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

if os.path.exists(URL_MODEL_PATH):
    try:
        url_model = joblib.load(URL_MODEL_PATH)
        if os.path.exists(URL_SCALER_PATH):
            url_scaler = joblib.load(URL_SCALER_PATH)
        logger.info("✓ URL IsolationForest model loaded successfully")
    except Exception as e:
        logger.warning(f"⚠ Could not load URL model: {e}")


def check_domain_age(domain: str) -> Optional[Dict[str, Any]]:
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


def scan_url_heuristics(url: str) -> Dict[str, Any]:
    if not url:
        return {"flagged": False, "reasons": [], "score": 0.0}
    
    reasons = []
    score_acc = 0.0
    url_l = url.lower().strip()
    
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
            if ':' in host: host = host.split(':')[0]
            domain = host
            tld = host.split('.')[-1] if '.' in host else ''
    except Exception:
        pass

    # 1. Trusted Domain handling
    if domain in TOP_TRUSTED or any(domain.endswith('.' + t) for t in TOP_TRUSTED):
        # We still scan but with a very high bar for flagging
        pass

    # 2. IP check
    if IP_REGEX.search(url_l):
        reasons.append("URL uses raw IP address")
        score_acc += 0.7

    # 3. Shorteners
    for sdom in SHORTENER_DOMAINS:
        if sdom in domain:
            reasons.append("URL uses a known shortener")
            score_acc += 0.7
            break

    # 4. Suspicious TLDs
    suspicious_tlds = {'xyz', 'top', 'club', 'info', 'online', 'site', 'icu', 'pw', 'ml', 'tk'}
    if tld in suspicious_tlds:
        reasons.append(f"Suspicious TLD: .{tld}")
        score_acc += 0.35

    # 5. Punycode
    if 'xn--' in url_l:
        reasons.append("Punycode or IDN detected (possible spoofing)")
        score_acc += 0.6

    # 6. Keywords
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in url_l:
            reasons.append(f"Suspicious keyword '{kw}' in URL")
            score_acc += 0.18

    # 7. Obfuscation (hyphens, length)
    hyphen_count = url_l.count('-')
    if hyphen_count > 5:
        reasons.append("Excessive hyphens suggest obfuscation")
        score_acc += 0.2
    if len(url_l) > 150:
        reasons.append("Very long URL (possible obfuscation)")
        score_acc += 0.15

    # 8. Unencrypted HTTP
    if url_l.startswith("http://") and not url_l.startswith("http://localhost"):
        reasons.append("Unencrypted HTTP (not HTTPS)")
        score_acc += 0.25

    # 9. Domain Reputation
    if ENABLE_DOMAIN_AGE_CHECK and domain:
        age_res = check_domain_age(domain)
        if age_res:
            reasons.append(age_res['reason'])
            score_acc += age_res['score']

    if ENABLE_SSL_CHECK and url_l.startswith('https'):
        ssl_res = check_ssl_certificate(url_l)
        if ssl_res:
            reasons.append(ssl_res['reason'])
            score_acc += ssl_res['score']

    # 10. Isolation Forest Model Score
    if url_model is not None:
        try:
            # 9 Advanced Features for iso_url_v1.joblib
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
            
            logger.info(f"DEBUG: URL features count = {len(feats)}, features = {feats}")
            
            X = np.array([feats], dtype=float)
            if url_scaler is not None:
                X = url_scaler.transform(X)
            
            raw = url_model.decision_function(X)
            val = float(-raw[0])
            model_score = 1 / (1 + math.exp(-val))
            
            # Combine heuristic score with model score (ensemble)
            # Model score is stronger for structural anomalies
            score_acc = 0.5 * score_acc + 0.5 * model_score
        except Exception as e:
            logger.warning(f"Model scoring failed: {e}")

    # Finalize
    final_score = min(1.0, score_acc)
    flagged = final_score >= 0.5
    
    if not reasons:
        reasons.append("No clear issues detected")
        
    return {
        "flagged": flagged,
        "reasons": reasons,
        "score": round(final_score, 2),
        "verdict": "malicious" if final_score >= 0.7 else "suspicious" if final_score >= 0.4 else "safe"
    }
