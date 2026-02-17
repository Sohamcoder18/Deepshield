#!/usr/bin/env python3
"""
MongoDB Connection Tester
Run this script to diagnose MongoDB connectivity issues
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env file
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', '')
MONGODB_DB_NAME = 'deepfakedatabase'

print("=" * 60)
print("MongoDB Connection Tester")
print("=" * 60)

print("\n1. Checking .env file...")
if MONGODB_URI:
    # Don't print the full URI as it contains credentials
    print(f"   ✓ MONGODB_URI found")
    print(f"   Length: {len(MONGODB_URI)} characters")
    
    if '<db_password>' in MONGODB_URI:
        print("   ✗ ERROR: URI contains <db_password> placeholder - needs to be replaced!")
    else:
        print("   ✓ No placeholder in URI")
else:
    print("   ✗ ERROR: MONGODB_URI not found in .env")
    exit(1)

print("\n2. Attempting MongoDB connection...")
try:
    # Create client with explicit timeout settings and SSL options
    mongo_client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        retryWrites=True,
        ssl=True,
        tlsAllowInvalidCertificates=True,
        w='majority'
    )
    
    print("   ✓ Client created")
    
    # Try to connect
    print("   Trying to connect...")
    mongo_client.admin.command('ping', maxTimeMS=5000)
    
    print("   ✓ Connected successfully!")
    
    # Get database
    mongo_db = mongo_client[MONGODB_DB_NAME]
    print(f"   ✓ Database '{MONGODB_DB_NAME}' selected")
    
    # List collections
    collections = mongo_db.list_collection_names()
    print(f"   ✓ Collections found: {collections}")
    
    # Check users collection
    if 'users' in collections:
        user_count = mongo_db['users'].count_documents({})
        print(f"   ✓ Users collection has {user_count} documents")
        
        # Show first user
        if user_count > 0:
            first_user = mongo_db['users'].find_one()
            print(f"\n   Sample user document:")
            for key, value in first_user.items():
                if key != '_id':
                    print(f"      {key}: {value}")
    else:
        print("   ✗ 'users' collection not found (will be created on first signup)")
    
    mongo_client.close()
    
    print("\n" + "=" * 60)
    print("✓ MongoDB Connection: SUCCESS")
    print("=" * 60)
    print("\nYou can now sign up and data should be stored in MongoDB!")
    
except Exception as e:
    print(f"\n   ✗ Connection failed!")
    print(f"   Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✗ MongoDB Connection: FAILED")
    print("=" * 60)
    
    print("\nPossible causes:")
    print("1. MongoDB cluster is PAUSED - Resume it on MongoDB Atlas")
    print("2. Network timeout - Check your internet connection")
    print("3. Credentials incorrect - Check .env MONGODB_URI")
    print("4. IP Whitelist - Add your IP to MongoDB Atlas whitelist")
    print("5. MongoDB service down - Check MongoDB Atlas status")
    
    exit(1)
