"""
Discover available Firestore databases in the Firebase project
"""
import os
import json
import subprocess
import sys

def discover_databases():
    """List all Firestore databases using gcloud CLI"""
    
    print("\n" + "="*70)
    print("FIRESTORE DATABASE DISCOVERY")
    print("="*70 + "\n")
    
    # Load project ID from credentials
    cred_path = 'database_info.json'
    if not os.path.exists(cred_path):
        cred_path = '../database_info.json'
    
    if not os.path.exists(cred_path):
        print("❌ database_info.json not found")
        return None
    
    with open(cred_path) as f:
        creds = json.load(f)
        project_id = creds['project_id']
    
    print(f"✓ Project ID: {project_id}\n")
    
    # Try 1: Use REST API with credentials
    print("Method 1: Using REST API with service account...\n")
    
    try:
        import google.auth
        from google.auth.transport.requests import Request
        from google.oauth2 import service_account
        import requests
        
        # Create credentials from service account file
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=scopes
        )
        
        # Get access token
        creds.refresh(Request())
        access_token = creds.token
        
        # Call Firestore Admin API
        url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            databases = data.get('databases', [])
            
            if databases:
                print(f"✓ Found {len(databases)} database(s):\n")
                for db in databases:
                    db_name = db['name'].split('/')[-1]
                    print(f"  Database Name: {db_name}")
                    print(f"  Full Path: {db['name']}")
                    print()
                
                return [db['name'].split('/')[-1] for db in databases]
            else:
                print("❌ No Firestore databases found\n")
                return None
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}\n")
            return None
            
    except Exception as e:
        print(f"⚠ REST API method failed: {type(e).__name__}\n")
    
    # Try 2: Use gcloud CLI
    print("Method 2: Using gcloud firestore:databases list...\n")
    
    try:
        # Try to use gcloud
        result = subprocess.run(
            ["gcloud", "firestore", "databases", "list", f"--project={project_id}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ gcloud output:")
            print(result.stdout)
            # Parse the output to extract database names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            databases = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if parts:
                        databases.append(parts[0])
            
            if databases:
                return databases
        else:
            print(f"⚠ gcloud error: {result.stderr}\n")
    except FileNotFoundError:
        print("⚠ gcloud CLI not installed\n")
    except subprocess.TimeoutExpired:
        print("⚠ gcloud command timed out\n")
    except Exception as e:
        print(f"⚠ gcloud method failed: {type(e).__name__}\n")
    
    # Try 3: Manual Firebase Console link
    print("Method 3: Manual check in Firebase Console\n")
    print(f"ℹ Go to: https://console.firebase.google.com/project/{project_id}/firestore")
    print("  1. Click 'Databases' in the left sidebar")
    print("  2. Look for your database name (should NOT be '(default)')")
    print("  3. Copy the database name\n")
    
    return None

if __name__ == "__main__":
    databases = discover_databases()
    
    if databases:
        print(f"\n{'='*70}")
        print(f"Found {len(databases)} database(s):")
        for db in databases:
            print(f"  - {db}")
        print(f"{'='*70}\n")
        
        print("Next steps:")
        print("  Run tests with the database name:")
        print(f"  python test_database.py --db={databases[0]}\n")
    else:
        print("\n❌ Could not automatically discover databases")
        print("   Please manually check Firebase Console and provide the database name\n")
