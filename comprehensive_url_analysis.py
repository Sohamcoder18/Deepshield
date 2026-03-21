#!/usr/bin/env python3
"""
Comprehensive URL Scanning Strategy for Malicious URLs
Multi-layered detection approach when Google Safe Browsing misses threats
"""

import requests
import sys
import os
import json
from urllib.parse import urlparse
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

API_KEY = "AIzaSyCb9e6CeitMGLCooN0TC08E3_rceF2efpQ"

# ============================================================================
# STRATEGY 1: Use Enhanced Phishing Scanner with Heuristics
# ============================================================================

def heuristic_analysis(url):
    """
    Detect malicious URLs using heuristic patterns when API checks miss them
    """
    url_lower = url.lower()
    risk_signals = []
    score = 0.0
    
    # Check 1: Domain reputation - iCloud phishing patterns
    if "icloud" in url_lower and "apple" not in url and ".br" in url_lower:
        risk_signals.append("Suspicious iCloud domain impersonation from non-Apple TLD")
        score += 0.4
    
    # Check 2: Newly registered or suspicious TLD
    suspicious_tlds = ['.top', '.xyz', '.tk', '.ml', '.ga', '.cf', 'br-icloud']
    for tld in suspicious_tlds:
        if tld in url_lower:
            risk_signals.append(f"Suspicious TLD or domain pattern: {tld}")
            score += 0.3
    
    # Check 3: Subdomain spoofing patterns
    parts = url_lower.split('/')[-1].split('.')
    if len(parts) > 3 and any(keyword in url_lower for keyword in ['verify', 'confirm', 'secure', 'login']):
        risk_signals.append("Excessive subdomains + suspicious keywords (possible phishing)")
        score += 0.35
    
    # Check 4: Domain misspelling common brands
    brand_impersonations = {
        'icloud': ['apple', 'icloud'],
        'paypal': ['paypal', 'ebay'],
        'amazon': ['amazon', 'aws'],
        'bank': ['bank', 'credit'],
        'microsoft': ['microsoft', 'office', 'outlook']
    }
    
    for keywords, brands in brand_impersonations.items():
        if any(keyword in url_lower for keyword in brands):
            if not any(brand in url_lower for brand in brands[1:]):
                risk_signals.append(f"Potential brand impersonation: {keywords}")
                score += 0.4
    
    return {
        'risk_signals': risk_signals,
        'risk_score': min(1.0, score),
        'verdict': 'MALICIOUS' if score >= 0.5 else 'SUSPICIOUS' if score >= 0.3 else 'SAFE'
    }


# ============================================================================
# STRATEGY 2: Use Enhanced Backend Phishing Scanner
# ============================================================================

def use_backend_scanner(url):
    """
    Use the enhanced phishing scanner from backend with blocklist
    """
    try:
        from backend.models.scanners.phishing_scanner import scan_url_heuristics
        result = scan_url_heuristics(url)
        return {
            'source': 'Backend Enhanced Scanner',
            'verdict': result['verdict'],
            'score': result['score'],
            'reasons': result['reasons'],
            'flagged': result['flagged']
        }
    except ImportError:
        return None


# ============================================================================
# STRATEGY 3: Add to Blocklist
# ============================================================================

def add_to_blocklist(domain):
    """
    Add confirmed malicious domain to blocklist for instant detection
    """
    blocklist_path = os.path.join(os.path.dirname(__file__), 
                                   'backend/data/url_list.json')
    
    try:
        # Load existing list
        if os.path.exists(blocklist_path):
            with open(blocklist_path, 'r') as f:
                data = json.load(f)
        else:
            data = {'blocklist': [], 'allowlist': []}
        
        # Add if not already present
        if domain not in data['blocklist']:
            data['blocklist'].append(domain)
            
            # Save updated list
            os.makedirs(os.path.dirname(blocklist_path), exist_ok=True)
            with open(blocklist_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
    except Exception as e:
        print(f"Error updating blocklist: {e}")
    
    return False


# ============================================================================
# STRATEGY 4: Google Safe Browsing API (with full URL)
# ============================================================================

def google_safe_browsing_check(url):
    """
    Check URL against Google Safe Browsing API
    """
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    
    payload = {
        "client": {
            "clientId": "malicious-url-detector",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    
    try:
        res = requests.post(endpoint, json=payload, timeout=5)
        data = res.json()
        
        if "matches" in data:
            return {
                'source': 'Google Safe Browsing',
                'verdict': 'MALICIOUS',
                'reasons': [f"Threat detected: {m.get('threatType', 'UNKNOWN')}" for m in data['matches']]
            }
        else:
            return {
                'source': 'Google Safe Browsing',
                'verdict': 'SAFE',
                'reasons': ['No threats detected in Google database']
            }
    except Exception as e:
        return {
            'source': 'Google Safe Browsing',
            'verdict': 'UNKNOWN',
            'error': str(e)
        }


# ============================================================================
# MAIN COMPREHENSIVE ANALYSIS
# ============================================================================

def comprehensive_url_analysis(url):
    """
    Comprehensive multi-layer detection strategy
    """
    print("=" * 80)
    print(f"COMPREHENSIVE URL ANALYSIS: {url}")
    print("=" * 80)
    
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    analysis_results = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'checks': []
    }
    
    # Layer 1: Heuristic Analysis
    print("\n[LAYER 1] Heuristic Pattern Analysis")
    print("-" * 80)
    heuristic_result = heuristic_analysis(url)
    print(f"Risk Score: {heuristic_result['risk_score']:.2f}")
    print(f"Verdict: {heuristic_result['verdict']}")
    print("Risk Signals:")
    for signal in heuristic_result['risk_signals']:
        print(f"  • {signal}")
    analysis_results['checks'].append({
        'type': 'Heuristic Analysis',
        'result': heuristic_result
    })
    
    # Layer 2: Google Safe Browsing API
    print("\n[LAYER 2] Google Safe Browsing API Check")
    print("-" * 80)
    google_result = google_safe_browsing_check(url)
    print(f"Status: {google_result.get('verdict', 'UNKNOWN')}")
    print(f"Source: {google_result['source']}")
    if google_result.get('reasons'):
        for reason in google_result['reasons']:
            print(f"  • {reason}")
    if google_result.get('error'):
        print(f"  Error: {google_result['error']}")
    analysis_results['checks'].append({
        'type': 'Google Safe Browsing',
        'result': google_result
    })
    
    # Layer 3: Backend Enhanced Scanner
    print("\n[LAYER 3] Backend Enhanced Phishing Scanner")
    print("-" * 80)
    backend_result = use_backend_scanner(url)
    if backend_result:
        print(f"Verdict: {backend_result['verdict'].upper()}")
        print(f"Score: {backend_result['score']:.2f}")
        print(f"Flagged: {backend_result['flagged']}")
        print("Reasons:")
        for reason in backend_result.get('reasons', [])[:3]:
            print(f"  • {reason}")
        analysis_results['checks'].append({
            'type': 'Backend Enhanced Scanner',
            'result': backend_result
        })
    else:
        print("Backend scanner not available (run from hackethon folder)")
    
    # Final Verdict
    print("\n" + "=" * 80)
    print("FINAL ANALYSIS")
    print("=" * 80)
    
    # Aggregate results
    verdicts = []
    if heuristic_result['verdict'] != 'SAFE':
        verdicts.append(('Heuristics', heuristic_result['verdict']))
    if google_result.get('verdict') != 'SAFE':
        verdicts.append(('Google Safe Browsing', google_result['verdict']))
    if backend_result and backend_result['verdict'] != 'safe':
        verdicts.append(('Backend Scanner', backend_result['verdict']))
    
    if verdicts:
        print(f"\n⚠️  MALICIOUS URL DETECTED")
        print(f"\nDetection layers:")
        for source, verdict in verdicts:
            print(f"  • {source}: {verdict}")
        analysis_results['final_verdict'] = 'MALICIOUS'
        analysis_results['recommendation'] = 'BLOCK THIS URL - Do not click. Report to security team.'
    else:
        print(f"\n✅ URL APPEARS SAFE")
        print("All detection layers passed.")
        analysis_results['final_verdict'] = 'SAFE'
        analysis_results['recommendation'] = 'URL appears safe to visit.'
    
    # Suggest adding to blocklist if malicious
    if analysis_results['final_verdict'] == 'MALICIOUS':
        domain = urlparse(url).netloc
        print(f"\n💡 RECOMMENDATION: Add '{domain}' to blocklist for instant future detection")
        print(f"   Command: add_to_blocklist('{domain}')")
    
    return analysis_results


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":
    # Test with the malicious URL
    test_url = "https://br-icloud.com.br"
    
    # Run comprehensive analysis
    results = comprehensive_url_analysis(test_url)
    
    # If malicious, add to blocklist
    if results['final_verdict'] == 'MALICIOUS':
        domain = urlparse(test_url).netloc
        print(f"\n[ACTION] Adding '{domain}' to blocklist...")
        if add_to_blocklist(domain):
            print(f"✓ Successfully added '{domain}' to blocklist")
        else:
            print(f"✗ Failed to add to blocklist")
    
    # Print JSON results
    print("\n" + "=" * 80)
    print("JSON RESULTS")
    print("=" * 80)
    print(json.dumps(results, indent=2))
