"""
List all Firestore databases in the Firebase project
"""
import os
import sys
import json
from google.cloud import firestore_admin

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def list_firestore_databases():
    """List all Firestore databases in the project"""
    
    print("\n" + "="*70)
    print("FIRESTORE DATABASE DISCOVERY")
    print("="*70 + "\n")
    
    try:
        # Initialize Firebase admin SDK
        credentials_path = 'database_info.json'
        if not os.path.exists(credentials_path):
            credentials_path = '../database_info.json'
        
        if not os.path.exists(credentials_path):
            print("❌ Error: database_info.json not found!")
            print("   Looked in: ./database_info.json and ../database_info.json")
            return
        
        from firebase_admin import credentials, initialize_app
        try:
            from firebase_admin import get_app
            get_app()
        except ValueError:
            cred = credentials.Certificate(credentials_path)
            initialize_app(cred)
        
        # Get project ID
        with open(credentials_path) as f:
            creds = json.load(f)
            project_id = creds['project_id']
        
        print(f"✓ Connected to Firebase project: {project_id}\n")
        
        # List databases using admin SDK
        client = firestore_admin.Client(project=project_id)
        databases = client.list_databases()
        
        print("Available Firestore Databases:\n")
        
        database_list = []
        for db in databases:
            db_name = db.name.split('/')[-1]  # Extract database name from full path
            db_type = db.database_type.name if hasattr(db, 'database_type') else 'FIRESTORE'
            
            database_list.append(db_name)
            
            print(f"  Name: {db_name}")
            print(f"  Type: {db_type}")
            print(f"  Full Path: {db.name}")
            print()
        
        if database_list:
            print("="*70)
            print(f"✓ Found {len(database_list)} database(s)")
            print("\nTo use a specific database, pass the name to test_database.py:")
            print(f"\nExample: python test_database.py --db {database_list[0]}")
            print("="*70 + "\n")
            
            # Update .env file
            print("\nOr set in .env file:")
            print(f'FIRESTORE_DATABASE="{database_list[0]}"\n')
            
            return database_list
        else:
            print("❌ No Firestore databases found in this project!")
            print("\nYou need to create a Firestore database:")
            print(f"  1. Go to: https://console.firebase.google.com/project/{project_id}")
            print("  2. Click 'Firestore Database' in the left menu")
            print("  3. Click 'Create Database'")
            print("  4. Choose 'Start in test mode'")
            print("  5. Click 'Enable'")
            print("\nThen run this script again to confirm.\n")
            return []
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}")
        print(f"   {str(e)}\n")
        
        print("Troubleshooting:")
        print("  - Ensure database_info.json exists with valid Firebase credentials")
        print("  - Ensure the service account has Firestore permissions")
        print("  - Try installing: pip install firebase-admin\n")

if __name__ == "__main__":
    databases = list_firestore_databases()
