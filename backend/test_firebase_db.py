"""
Test firebase-admin multi-database support
"""
import firebase_admin
from firebase_admin import credentials, firestore
import inspect
import json

# Load credentials
with open('database_info.json') as f:
    cred_dict = json.load(f)
    project_id = cred_dict['project_id']

cred = credentials.Certificate('database_info.json')

# Check if app exists
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred)

# Test 1: Check firestore.client() signature
print("firestore.client() signature:")
print(inspect.signature(firestore.client))
print()

# Test 2: Check available parameters
print("firestore.client() docstring:")
print(firestore.client.__doc__)
print()

# Test 3: Try to connect with database parameter
print("Attempting to connect with database='default'...")
try:
    db = firestore.client(database='default')
    print("✓ Successfully created client with database='default'")
    print(f"  Client: {db}")
    print(f"  Client type: {type(db)}")
    
    # Try a test operation
    print("\nTesting read operation...")
    collections = db.collections()
    collections_list = list(collections)
    print(f"✓ Collections found: {len(collections_list)}")
    for col in collections_list[:5]:
        print(f"  - {col.id}")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")

print("\n" + "="*70)
