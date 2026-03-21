#!/usr/bin/env python3
"""
Test the integrated pretrained model for URL detection
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.scanners.phishing_scanner import scan_url_heuristics

def test_pretrained_model():
    """Test URL scanning with integrated pretrained model"""
    
    print("=" * 80)
    print("TESTING PRETRAINED MODEL INTEGRATION")
    print("=" * 80)
    
    test_cases = [
        {
            "url": "https://www.google.com",
            "expected": "safe",
            "description": "Safe URL"
        },
        {
            "url": "https://www.amazon.com",
            "expected": "safe",
            "description": "Safe URL"
        },
        {
            "url": "https://secure-paypal-verify.xyz",
            "expected": "malicious",
            "description": "Blocklisted phishing domain"
        },
        {
            "url": "https://br-icloud.com.br",
            "expected": "malicious",
            "description": "Blocklisted iCloud phishing"
        },
        {
            "url": "https://confirm-amazon-login.tk",
            "expected": "malicious",
            "description": "Blocklisted Amazon phishing"
        },
        {
            "url": "https://bit.ly/confirm-payment",
            "expected": "suspicious",
            "description": "Shortener with phishing keywords"
        },
        {
            "url": "http://192.168.1.100/secure-login",
            "expected": "suspicious",
            "description": "Raw IP with suspicious keywords"
        },
        {
            "url": "https://upi-verify-update.icu/login",
            "expected": "malicious",
            "description": "UPI phishing with suspicious TLD"
        },
        {
            "url": "https://github.com",
            "expected": "safe",
            "description": "Legitimate development platform"
        },
        {
            "url": "https://fake-bank-account-verify.xyz/confirm",
            "expected": "malicious",
            "description": "Multiple suspicious signals"
        },
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        url = test['url']
        expected = test['expected']
        description = test['description']
        
        # Scan URL
        result = scan_url_heuristics(url)
        verdict = result['verdict']
        score = result['score']
        flagged = result['flagged']
        
        # Check result
        is_pass = verdict == expected
        if is_pass:
            passed += 1
            status = "PASS"
            symbol = "[OK]"
        else:
            failed += 1
            status = "FAIL"
            symbol = "[XX]"
        
        print(f"\n{symbol} Test: {description}")
        print(f"  URL: {url}")
        print(f"  Expected: {expected.upper():12} | Actual: {verdict.upper():12} | [{status}]")
        print(f"  Score: {score:.2f} | Flagged: {flagged}")
        
        # Show model info
        checks = result.get('checks_run', [])
        if 'pretrained_model' in checks:
            print(f"  [*] Pretrained model used")
        elif 'ml_model' in checks:
            print(f"  [*] Fallback ML model used")
        
        # Show top reasons
        reasons = result.get('reasons', [])
        if reasons:
            print(f"  Reasons: {reasons[0]}")
            if len(reasons) > 1:
                print(f"           {reasons[1]}")
    
    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("\n[OK] ALL TESTS PASSED - Pretrained model is working correctly!")
    else:
        print(f"\n[XX] {failed} test(s) failed - Review results above")
    
    return failed == 0

if __name__ == "__main__":
    success = test_pretrained_model()
    sys.exit(0 if success else 1)
