"""Test that app imports without MongoDB errors"""
import sys
import os

print("\n" + "="*70)
print("Testing app.py imports...")
print("="*70 + "\n")

try:
    print("Importing app module...")
    from app import app, firestore_manager
    print("✓ Successfully imported app module\n")
    
    print(f"Firestore Manager Status:")
    print(f"  - Available: {firestore_manager.firestore_available}")
    print(f"  - Database: {firestore_manager.database_name}")
    print(f"  - Has db client: {firestore_manager.db is not None}\n")
    
    print("Testing send_otp endpoint signature...")
    # Check if the endpoint exists
    rules = [rule for rule in app.url_map.iter_rules() if 'send_otp' in rule.rule]
    if rules:
        print(f"✓ Found send_otp endpoint: {rules[0].rule}\n")
    else:
        print("❌ send_otp endpoint not found\n")
    
    print("Testing authentication endpoints...")
    auth_endpoints = [str(rule) for rule in app.url_map.iter_rules() if '/api/auth/' in rule.rule]
    for endpoint in sorted(auth_endpoints):
        print(f"  ✓ {endpoint}")
    
    print("\n" + "="*70)
    print("✅ SUCCESS: App imports correctly without MongoDB errors!")
    print("="*70 + "\n")
    
except NameError as e:
    if 'mongo_db' in str(e):
        print(f"❌ ERROR: MongoDB reference still exists: {e}\n")
    else:
        print(f"❌ ERROR: {type(e).__name__}: {e}\n")
except Exception as e:
    import traceback
    print(f"❌ ERROR: {type(e).__name__}: {e}\n")
    traceback.print_exc()

