#!/usr/bin/env python
"""Test Brevo email configuration"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv('BREVO_API_KEY', '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')

print("=" * 60)
print("BREVO EMAIL CONFIGURATION TEST")
print("=" * 60)

# Test 1: Check API connectivity
print("\n[TEST 1] Checking API connectivity...")
try:
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    response = requests.get("https://api.brevo.com/v3/account", headers=headers, timeout=5)
    if response.status_code == 200:
        account_info = response.json()
        print(f"✅ API Connected Successfully!")
        print(f"   Account Email: {account_info.get('email', 'N/A')}")
        print(f"   Account Plan: {account_info.get('plan', 'N/A')}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Connection Error: {str(e)}")

# Test 2: Get verified sender emails
print("\n[TEST 2] Checking verified sender emails...")
try:
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY
    }
    response = requests.get("https://api.brevo.com/v3/senders", headers=headers, timeout=5)
    if response.status_code == 200:
        senders = response.json().get('senders', [])
        if senders:
            print(f"✅ Found {len(senders)} verified sender(s):")
            for sender in senders:
                print(f"   - {sender.get('name', 'No Name')} <{sender.get('email', 'N/A')}>")
                print(f"     Status: {sender.get('active', False)}")
        else:
            print("⚠️  No verified senders found. You need to verify a sender email first.")
            print("   Go to: https://app.brevo.com/settings/senders")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 3: Send test email
print("\n[TEST 3] Sending test email...")
test_email = input("Enter your email to test: ").strip().lower()

if test_email and '@' in test_email:
    try:
        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        payload = {
            "sender": {"name": "DeepShield", "email": "noreply@deepshield.com"},
            "to": [{"email": test_email}],
            "subject": "DeepShield Test Email",
            "htmlContent": "<h1>Test Email</h1><p>If you receive this, Brevo is working!</p>"
        }
        
        response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        if response.status_code == 201:
            print("✅ Email sent successfully!")
            print("   Check your email inbox and spam folder")
        else:
            print(f"❌ Failed to send: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
else:
    print("⚠️  Invalid email entered")

print("\n" + "=" * 60)
print("TROUBLESHOOTING TIPS:")
print("=" * 60)
print("""
1. Check email SPAM/JUNK folder first
2. Verify sender email in Brevo:
   - Go to: https://app.brevo.com/settings/senders
   - Add and verify your sender email address
3. Use a real email address as sender (e.g., your@domain.com)
4. Check Brevo account status and credits
5. Verify API key is correct and has email permissions
""")
print("=" * 60)
