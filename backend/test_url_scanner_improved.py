#!/usr/bin/env python3
"""
Test script to verify the improved URL scanner with Google Safe Browsing API
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.scanners.phishing_scanner import scan_url_heuristics

# Test cases
test_urls = [
    # Safe URLs
    ("https://www.google.com", "safe"),
    ("https://www.amazon.com", "safe"),
    ("https://github.com", "safe"),
    
    # Known blocklisted domains (MALICIOUS)
    ("https://secure-paypal-verify.xyz", "malicious"),
    ("https://confirm-amazon-login.tk", "malicious"),
    ("https://upi-verify-update.icu", "malicious"),
    
    # URLs with multiple high-risk signals (MALICIOUS)
    ("http://verify-account-urgently.xyz/login?token=123", "malicious"),
    ("http://bank-verify.tk/secure/password", "malicious"),
    ("https://confirm-payment-xn--verify.xyz", "malicious"),
    ("http://192.168.1.1/login", "malicious"),
    ("https://fake-bank-account-verify-update.xyz/upi/confirm", "malicious"),
    ("http://secure-login-verify-update-payment.ml/upi-account/confirm-now", "malicious"),
    
    # Suspicious URLs with fewer risk signals
    ("https://bit.ly/malicious-link", "suspicious"),
]

def test_url_scanner():
    print("=" * 80)
    print("URL SCANNER TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for url, expected_verdict in test_urls:
        result = scan_url_heuristics(url)
        actual_verdict = result['verdict']
        score = result['score']
        flagged = result['flagged']
        checks = result.get('checks_run', [])
        
        # Determine pass/fail
        is_pass = actual_verdict == expected_verdict
        if is_pass:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        
        print("\n" + "-" * 80)
        print(f"URL: {url}")
        print(f"Expected: {expected_verdict.upper():12} | Actual: {actual_verdict.upper():12} | [{status}]")
        print(f"Score: {score:.2f} | Flagged: {flagged}")
        print(f"Checks run: {', '.join(checks)}")
        print(f"Reasons:")
        for reason in result['reasons']:
            print(f"  - {reason}")
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(test_urls)} tests")
    print("=" * 80)
    
    return failed == 0

if __name__ == "__main__":
    success = test_url_scanner()
    sys.exit(0 if success else 1)
