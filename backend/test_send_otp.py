"""Test the send_otp endpoint with Firestore"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, firestore_manager
import json

print("\n" + "="*70)
print("Testing send_otp endpoint")
print("="*70 + "\n")

# Test data
test_data = {
    "email": "newuser@test.com",
    "isSignup": True
}

try:
    with app.test_client() as client:
        print(f"Firestore Available: {firestore_manager.firestore_available}")
        print(f"Firestore Database: {firestore_manager.database_name}\n")
        
        print("Sending OTP request...")
        response = client.post('/api/auth/send-otp', 
                             json=test_data,
                             content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: send_otp endpoint is working!")
        else:
            print(f"\n⚠️  Endpoint returned status {response.status_code}")
            
except Exception as e:
    import traceback
    print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
    traceback.print_exc()

print("\n" + "="*70)
