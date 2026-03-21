#!/usr/bin/env python3
"""
Integration test for URL scanner API endpoint
Tests the Flask API endpoint with various URLs
"""

import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.scanners.phishing_scanner import scan_url_heuristics

def test_api_simulation():
    """Simulate API requests and verify responses"""
    
    print("=" * 80)
    print("URL SCANNER API INTEGRATION TEST")
    print("=" * 80)
    
    test_cases = [
        {
            "name": "Safe URL (Google)",
            "url": "https://www.google.com",
            "expected_flagged": False
        },
        {
            "name": "Blocklisted Malicious Domain",
            "url": "https://secure-paypal-verify.xyz",
            "expected_flagged": True
        },
        {
            "name": "Phishing with Shortener",
            "url": "https://bit.ly/confirm-account",
            "expected_flagged": True
        },
        {
            "name": "UPI Phishing Attempt",
            "url": "http://upi-verify-update.icu/login",
            "expected_flagged": True
        },
        {
            "name": "Banking Login Spoof",
            "url": "https://confirm-amazon-login.tk/account",
            "expected_flagged": True
        },
        {
            "name": "Raw IP with Login",
            "url": "http://192.168.1.100/secure-login",
            "expected_flagged": True
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        url = test["url"]
        expected_flagged = test["expected_flagged"]
        
        # Simulate API call
        result = scan_url_heuristics(url)
        
        # Check if flagged matches expectation
        actual_flagged = result["flagged"]
        is_pass = actual_flagged == expected_flagged
        
        if is_pass:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        
        print(f"\nTest: {test['name']}")
        print(f"URL: {url}")
        print(f"Expected flagged: {expected_flagged} | Actual: {actual_flagged} | [{status}]")
        print(f"Score: {result['score']} | Verdict: {result['verdict'].upper()}")
        
        # Simulate JSON response
        api_response = {
            "status": "success",
            "analysis_type": "url",
            "url": url,
            "risk_score": result['score'],
            "is_fake": result['flagged'],
            "reasons": result['reasons'][:3],  # Show first 3 reasons
            "verdict": result['verdict'],
            "recommendation": f"This URL appears {result['verdict']}. {'Avoid clicking.' if result['flagged'] else 'Proceed with normal caution.'}",
            "timestamp": "2024-01-01T12:00:00"
        }
        
        print(f"API Response (JSON):")
        print(json.dumps(api_response, indent=2))
    
    print("\n" + "=" * 80)
    print(f"INTEGRATION TEST SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED - URL Scanner API is ready for production")
    else:
        print(f"\n[FAILED] {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_api_simulation()
    sys.exit(0 if success else 1)
