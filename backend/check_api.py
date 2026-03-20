#!/usr/bin/env python3
"""
Check if Firestore API is available and list database IDs
"""
import subprocess
import json

def check_firestore_api():
    print("=" * 60)
    print("Checking Firestore API Status")
    print("=" * 60)
    
    print("\n[Step 1] Click here to enable Cloud Firestore API:")
    print("  https://console.cloud.google.com/apis/library/firestore.googleapis.com?project=deepfake-5e76b")
    print("  Click the 'Enable' button if not already enabled")
    
    print("\n[Step 2] Verify the database ID in Firebase Console:")
    print("  https://console.cloud.google.com/firestore/databases?project=deepfake-5e76b")
    print("  Look at the database URL or settings - note the exact database name")
    
    print("\n[Step 3] If database name is NOT 'default', run this command:")
    print("  cd d:\\hackethon\\backend")
    print("  python -c \"from dotenv import load_dotenv; load_dotenv(); print('Update FIRESTORE_DATABASE in .env')\"")
    
    print("\n[Step 4] Common database IDs to check for:")
    print("  - default")
    print("  - (default)")
    print("  Check the database dropdown in Firebase Console to see the exact name")

if __name__ == '__main__':
    check_firestore_api()
