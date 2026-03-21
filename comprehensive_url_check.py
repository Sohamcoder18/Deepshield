#!/usr/bin/env python3
"""
Comprehensive URL analysis using Google Safe Browsing + Enhanced Phishing Scanner
Tests "br-icloud.com.br" with multiple detection methods
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import requests
from models.scanners.phishing_scanner import scan_url_heuristics

API_KEY = "AIzaSyCb9e6CeitMGLCooN0TC08E3_rceF2efpQ"
url = "https://br-icloud.com.br"

print("=" * 80)
print("COMPREHENSIVE URL SAFETY ANALYSIS")
print("=" * 80)
print(f"\nURL: {url}\n")

# ========== TEST 1: GOOGLE SAFE BROWSING API ==========
print("1. GOOGLE SAFE BROWSING API Check")
print("-" * 80)

endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
payload = {
  "client": {
    "clientId": "your-app",
    "clientVersion": "1.0"
  },
  "threatInfo": {
    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
    "platformTypes": ["ANY_PLATFORM"],
    "threatEntryTypes": ["URL"],
    "threatEntries": [{"url": url}]
  }
}

try:
    res = requests.post(endpoint, json=payload, timeout=5)
    google_data = res.json()
    
    if "error" in google_data:
        print(f"❌ API Error: {google_data['error']}")
    elif "matches" in google_data:
        threat_types = [m.get('threatType', 'UNKNOWN') for m in google_data['matches']]
        print(f"⚠️ DANGEROUS - Threats detected: {', '.join(threat_types)}")
    else:
        print(f"✅ NOT FLAGGED by Google Safe Browsing")
        print(f"   Response: {google_data}")
except Exception as e:
    print(f"❌ Error: {e}")

# ========== TEST 2: ENHANCED PHISHING SCANNER ==========
print("\n2. ENHANCED PHISHING SCANNER Analysis")
print("-" * 80)

try:
    result = scan_url_heuristics(url)
    
    print(f"Verdict: {result['verdict'].upper()}")
    print(f"Risk Score: {result['score']}")
    print(f"Flagged: {result['flagged']}")
    print(f"\nDetailed Analysis:")
    for i, reason in enumerate(result['reasons'], 1):
        print(f"  {i}. {reason}")
    
    print(f"\nChecks Run: {', '.join(result.get('checks_run', []))}")
    
except Exception as e:
    print(f"❌ Scanner Error: {e}")

# ========== SUMMARY ==========
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Note: If Google Safe Browsing returns "NOT FLAGGED" but the Enhanced Scanner 
shows MALICIOUS/SUSPICIOUS, it means:

1. The domain may be newly created (not yet in Google's database)
2. The domain exhibits phishing/malware characteristics
3. The domain uses suspicious patterns
4. The domain may be similar to legitimate services (spoofing)

RECOMMENDATION: Trust the Enhanced Scanner for phishing detection!
""")
