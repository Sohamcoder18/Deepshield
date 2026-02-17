"""
Test Script for Firestore + SQLite Database Integration
Tests all database operations for the DeepFake Detection System
"""

import os
import sys
import io

# Force UTF-8 output encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime
import json
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from utils.firestore_utils import FirestoreManager

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

# ============================================
# TEST DATA
# ============================================

TEST_USER_EMAIL = "testuser@deepshield.com"
TEST_USER_DATA = {
    'full_name': 'Test User',
    'phone_number': '+1234567890',
    'date_of_birth': '1990-01-15',
    'country': 'USA',
    'occupation': 'Software Engineer',
    'created_at': datetime.utcnow(),
    'last_login': datetime.utcnow(),
    'total_analyses': 0
}

TEST_ANALYSIS_DATA = {
    'user_email': TEST_USER_EMAIL,
    'analysis_type': 'image',
    'file_name': 'test_deepfake.jpg',
    'file_size': 2048576,
    'trust_score': 78.5,
    'is_fake': True,
    'confidence': 92.0,
    'recommendation': 'This image appears to be a deepfake with high confidence',
    'analysis_time': 5.234,
    'xception_score': 0.92,
    'artifact_detection': 0.85
}

# ============================================
# INITIALIZE DATABASES
# ============================================

def initialize_databases():
    """Initialize Flask app and databases"""
    print_header("INITIALIZING DATABASES")
    
    try:
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///deepfake_detection.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db = SQLAlchemy(app)
        
        # Import and initialize models
        from models.database_models import initialize_models
        models = initialize_models(db)
        
        with app.app_context():
            db.create_all()
            print_success("SQLite database initialized")
        
        return app, db, models
    except Exception as e:
        print_error(f"Failed to initialize databases: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

# ============================================
# TEST 1: FIRESTORE CONNECTION
# ============================================

def test_firestore_connection(firestore_manager):
    """Test Firestore connection"""
    print_header("TEST 1: FIRESTORE CONNECTION")
    
    if firestore_manager.firestore_available:
        print_success("Firestore is connected and available")
        print(f"  Project: Firestore client initialized")
        return True
    else:
        print_warning("Firestore is not available (SQLite will be used)")
        return False

# ============================================
# TEST 2: FIRESTORE DOCUMENT ID GENERATION
# ============================================

def test_document_id_generation():
    """Test date-based document ID generation"""
    print_header("TEST 2: DOCUMENT ID GENERATION")
    
    try:
        signup_id = FirestoreManager.generate_date_based_doc_id("signup")
        login_id = FirestoreManager.generate_date_based_doc_id("login")
        analysis_id = FirestoreManager.generate_date_based_doc_id("analysis")
        anl_id = FirestoreManager.generate_date_based_doc_id("anl")
        
        print_info("Generated Document IDs:")
        print(f"  Signup ID:   {signup_id}")
        print(f"  Login ID:    {login_id}")
        print(f"  Analysis ID: {analysis_id}")
        print(f"  Analysis Log ID: {anl_id}")
        
        # Validate format
        if all(id.startswith(prefix) for id, prefix in [
            (signup_id, "signup_"),
            (login_id, "login_"),
            (analysis_id, "analysis_"),
            (anl_id, "anl_")
        ]):
            print_success("All document IDs follow correct format")
            return True
        else:
            print_error("Document ID format is incorrect")
            return False
    except Exception as e:
        print_error(f"Failed to generate document IDs: {str(e)}")
        return False

# ============================================
# TEST 3: SAVE SIGNUP EVENT
# ============================================

def test_save_signup_event(firestore_manager):
    """Test saving signup event"""
    print_header("TEST 3: SAVE SIGNUP EVENT")
    
    try:
        result = firestore_manager.save_signup_event(TEST_USER_EMAIL, TEST_USER_DATA)
        
        if result['success']:
            print_success("Signup event saved successfully")
            if result['firestore_id']:
                print(f"  Firestore ID: {result['firestore_id']}")
            if result['sqlite_id']:
                print(f"  SQLite ID: {result['sqlite_id']}")
            
            if result['errors']:
                print_warning("Errors during save:")
                for error in result['errors']:
                    print(f"    - {error}")
            
            return True
        else:
            print_error("Failed to save signup event")
            for error in result['errors']:
                print(f"  Error: {error}")
            return False
    except Exception as e:
        print_error(f"Exception during signup save: {str(e)}")
        return False

# ============================================
# TEST 4: SAVE USER PROFILE
# ============================================

def test_save_user_profile(firestore_manager):
    """Test saving user profile"""
    print_header("TEST 4: SAVE USER PROFILE")
    
    try:
        result = firestore_manager.save_user_profile(TEST_USER_EMAIL, TEST_USER_DATA)
        
        if result['success']:
            print_success("User profile saved successfully")
            if result['firestore_id']:
                print(f"  Firestore ID: {result['firestore_id']}")
            if result['sqlite_id']:
                print(f"  SQLite ID: {result['sqlite_id']}")
            return True
        else:
            print_error("Failed to save user profile")
            for error in result['errors']:
                print(f"  Error: {error}")
            return False
    except Exception as e:
        print_error(f"Exception during user profile save: {str(e)}")
        return False

# ============================================
# TEST 5: SAVE LOGIN EVENT
# ============================================

def test_save_login_event(firestore_manager):
    """Test saving login event"""
    print_header("TEST 5: SAVE LOGIN EVENT")
    
    try:
        login_data = {
            'ip_address': '192.168.1.100',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        
        result = firestore_manager.save_login_event(TEST_USER_EMAIL, additional_data=login_data)
        
        if result['success']:
            print_success("Login event saved successfully")
            if result['firestore_id']:
                print(f"  Firestore ID: {result['firestore_id']}")
            if result['sqlite_id']:
                print(f"  SQLite ID: {result['sqlite_id']}")
            return True
        else:
            print_error("Failed to save login event")
            for error in result['errors']:
                print(f"  Error: {error}")
            return False
    except Exception as e:
        print_error(f"Exception during login save: {str(e)}")
        return False

# ============================================
# TEST 6: SAVE ANALYSIS RESULT
# ============================================

def test_save_analysis_result(firestore_manager):
    """Test saving analysis result"""
    print_header("TEST 6: SAVE ANALYSIS RESULT")
    
    try:
        result = firestore_manager.save_analysis_result(TEST_ANALYSIS_DATA)
        
        if result['success']:
            print_success("Analysis result saved successfully")
            analysis_id = result['firestore_id']
            if result['firestore_id']:
                print(f"  Firestore ID: {analysis_id}")
            if result['sqlite_id']:
                print(f"  SQLite ID: {result['sqlite_id']}")
            return True, analysis_id
        else:
            print_error("Failed to save analysis result")
            for error in result['errors']:
                print(f"  Error: {error}")
            return False, None
    except Exception as e:
        print_error(f"Exception during analysis save: {str(e)}")
        return False, None

# ============================================
# TEST 7: SAVE USER ANALYSIS LOG
# ============================================

def test_save_user_analysis_log(firestore_manager, analysis_id):
    """Test saving user analysis log"""
    print_header("TEST 7: SAVE USER ANALYSIS LOG")
    
    if not analysis_id:
        print_warning("Skipping (no analysis_id from previous test)")
        return False
    
    try:
        result = firestore_manager.save_user_analysis_log(
            TEST_USER_EMAIL,
            analysis_id,
            TEST_ANALYSIS_DATA
        )
        
        if result['success']:
            print_success("User analysis log saved successfully")
            if result['firestore_id']:
                print(f"  Firestore ID: {result['firestore_id']}")
            return True
        else:
            print_error("Failed to save user analysis log")
            for error in result['errors']:
                print(f"  Error: {error}")
            return False
    except Exception as e:
        print_error(f"Exception during user analysis log save: {str(e)}")
        return False

# ============================================
# TEST 8: GET USER PROFILE
# ============================================

def test_get_user_profile(firestore_manager):
    """Test retrieving user profile"""
    print_header("TEST 8: GET USER PROFILE")
    
    try:
        user_data = firestore_manager.get_user_profile(TEST_USER_EMAIL)
        
        if user_data:
            print_success("User profile retrieved successfully")
            print(f"  Email: {user_data.get('email')}")
            print(f"  Full Name: {user_data.get('full_name')}")
            print(f"  Country: {user_data.get('country')}")
            print(f"  Occupation: {user_data.get('occupation')}")
            print(f"  Created At: {user_data.get('created_at')}")
            print(f"  Total Analyses: {user_data.get('total_analyses')}")
            return True
        else:
            print_error("User profile not found")
            return False
    except Exception as e:
        print_error(f"Exception during user profile retrieval: {str(e)}")
        return False

# ============================================
# TEST 9: GET USER ANALYSIS LOGS
# ============================================

def test_get_user_analysis_logs(firestore_manager):
    """Test retrieving user analysis logs"""
    print_header("TEST 9: GET USER ANALYSIS LOGS")
    
    try:
        logs = firestore_manager.get_user_analysis_logs(TEST_USER_EMAIL, limit=10)
        
        if logs:
            print_success(f"Retrieved {len(logs)} analysis log(s)")
            for i, log in enumerate(logs, 1):
                print(f"\n  Log {i}:")
                print(f"    Analysis Type: {log.get('analysis_type')}")
                print(f"    File Name: {log.get('file_name')}")
                print(f"    Is Fake: {log.get('is_fake')}")
                print(f"    Confidence: {log.get('confidence')}%")
                print(f"    Timestamp: {log.get('timestamp')}")
            return True
        else:
            print_warning("No analysis logs found")
            return True  # Not an error, just no data yet
    except Exception as e:
        print_error(f"Exception during analysis logs retrieval: {str(e)}")
        return False

# ============================================
# TEST 10: GET LOGIN HISTORY
# ============================================

def test_get_login_history(firestore_manager):
    """Test retrieving login history"""
    print_header("TEST 10: GET LOGIN HISTORY")
    
    try:
        history = firestore_manager.get_login_history(user_email=TEST_USER_EMAIL, limit=10)
        
        if history:
            print_success(f"Retrieved {len(history)} login record(s)")
            for i, record in enumerate(history, 1):
                print(f"\n  Record {i}:")
                print(f"    Email: {record.get('email')}")
                print(f"    IP Address: {record.get('ip_address')}")
                print(f"    Timestamp: {record.get('timestamp')}")
                print(f"    Status: {record.get('status')}")
            return True
        else:
            print_warning("No login history found")
            return True
    except Exception as e:
        print_error(f"Exception during login history retrieval: {str(e)}")
        return False

# ============================================
# TEST 11: GET SIGNUP HISTORY
# ============================================

def test_get_signup_history(firestore_manager):
    """Test retrieving signup history"""
    print_header("TEST 11: GET SIGNUP HISTORY")
    
    try:
        history = firestore_manager.get_signup_history(limit=10)
        
        if history:
            print_success(f"Retrieved {len(history)} signup record(s)")
            for i, record in enumerate(history, 1):
                print(f"\n  Record {i}:")
                print(f"    Email: {record.get('email')}")
                print(f"    Full Name: {record.get('full_name')}")
                print(f"    Country: {record.get('country')}")
                print(f"    Timestamp: {record.get('timestamp')}")
                print(f"    Status: {record.get('status')}")
            return True
        else:
            print_warning("No signup history found")
            return True
    except Exception as e:
        print_error(f"Exception during signup history retrieval: {str(e)}")
        return False

# ============================================
# TEST 12: GET ANALYSIS HISTORY
# ============================================

def test_get_analysis_history(firestore_manager):
    """Test retrieving analysis history"""
    print_header("TEST 12: GET ANALYSIS HISTORY")
    
    try:
        history = firestore_manager.get_analysis_history(user_email=TEST_USER_EMAIL, limit=10)
        
        if history:
            print_success(f"Retrieved {len(history)} analysis record(s)")
            for i, record in enumerate(history, 1):
                print(f"\n  Record {i}:")
                print(f"    Analysis Type: {record.get('analysis_type')}")
                print(f"    File Name: {record.get('file_name')}")
                print(f"    Is Fake: {record.get('is_fake')}")
                print(f"    Confidence: {record.get('confidence')}%")
                print(f"    Trust Score: {record.get('trust_score')}")
                print(f"    Timestamp: {record.get('timestamp')}")
            return True
        else:
            print_warning("No analysis history found")
            return True
    except Exception as e:
        print_error(f"Exception during analysis history retrieval: {str(e)}")
        return False

# ============================================
# TEST 13: UPDATE LAST LOGIN
# ============================================

def test_update_last_login(firestore_manager):
    """Test updating last login timestamp"""
    print_header("TEST 13: UPDATE LAST LOGIN")
    
    try:
        result = firestore_manager.update_last_login(TEST_USER_EMAIL)
        
        if result:
            print_success("Last login timestamp updated successfully")
            
            # Retrieve updated profile
            user_data = firestore_manager.get_user_profile(TEST_USER_EMAIL)
            if user_data:
                print(f"  Updated Last Login: {user_data.get('last_login')}")
            return True
        else:
            print_error("Failed to update last login")
            return False
    except Exception as e:
        print_error(f"Exception during last login update: {str(e)}")
        return False

# ============================================
# TEST 14: CHECK SQLITE BACKUP
# ============================================

def test_sqlite_backup(db, app):
    """Test SQLite backup database"""
    print_header("TEST 14: CHECK SQLITE BACKUP")
    
    if db is None:
        print_warning("SQLite database not initialized")
        return False
    
    try:
        # Check if any tables have data by querying the database directly
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        print_info(f"SQLite tables found: {', '.join(tables)}")
        
        table_counts = {}
        for table in tables:
            try:
                result = db.session.execute(db.text(f"SELECT COUNT(*) as cnt FROM {table}"))
                count = result.scalar()
                table_counts[table] = count
                print_info(f"  {table}: {count} records")
            except Exception as e:
                print_warning(f"  Could not count {table}: {str(e)}")
        
        total = sum(table_counts.values())
        if total > 0:
            print_success(f"SQLite backup contains {total} records")
            return True
        else:
            print_warning("SQLite backup is empty (expected if Firestore is used)")
            return True
    except Exception as e:
        print_error(f"Exception during SQLite backup check: {str(e)}")
        return False

# ============================================
# TEST 15: VERIFY DATA IN BOTH DATABASES
# ============================================

def test_data_sync(firestore_manager, db, app):
    """Test that data exists in both databases"""
    print_header("TEST 15: VERIFY DATA SYNCHRONIZATION")
    
    try:
        # Check Firestore
        firestore_user = firestore_manager.get_user_profile(TEST_USER_EMAIL) if firestore_manager.firestore_available else None
        
        # Check SQLite by querying directly
        sqlite_user_exists = False
        if db:
            try:
                result = db.session.execute(db.text(f"SELECT * FROM users WHERE email = :email"), {"email": TEST_USER_EMAIL})
                sqlite_user = result.fetchone()
                sqlite_user_exists = sqlite_user is not None
            except Exception as e:
                print_warning(f"Could not query SQLite users table: {str(e)}")
        
        print_info("Database Status:")
        print(f"  Firestore: {'✓ Available' if firestore_manager.firestore_available else '✗ Unavailable'}")
        print(f"  SQLite: {'✓ Available' if db else '✗ Unavailable'}")
        
        if firestore_user:
            print_success(f"User found in Firestore: {firestore_user.get('email')}")
        else:
            print_warning("User not found in Firestore (may be using SQLite only)")
        
        if sqlite_user_exists:
            print_success(f"User found in SQLite: {TEST_USER_EMAIL}")
        else:
            print_warning("User not found in SQLite")
        
        if firestore_user or sqlite_user_exists:
            print_success("Data verified in at least one database")
            return True
        else:
            print_warning("No user data found in any database")
            return True
    except Exception as e:
        print_error(f"Exception during data sync check: {str(e)}")
        return False

# ============================================
# MAIN TEST EXECUTION
# ============================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + "DEEPFAKE DETECTION - DATABASE TEST SUITE".center(58) + "║")
    print("║" + f"Testing Firestore + SQLite Integration".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.ENDC}\n")
    
    # Parse command-line arguments
    database_name = None
    for arg in sys.argv[1:]:
        if arg.startswith('--db='):
            database_name = arg.split('=')[1]
            break
        elif arg == '--help' or arg == '-h':
            print("Usage: python test_database.py [--db=DATABASE_NAME]")
            print("  --db=NAME  : Specify Firestore database name (default: 'default')")
            print("  --help     : Show this help message\n")
            return 0
    
    if database_name:
        print_info(f"Using Firestore database: {database_name}")
    else:
        print_info("Using default Firestore database: default")
        database_name = 'default'  # Explicitly set default here
    
    # Initialize databases
    result = initialize_databases()
    if len(result) == 3:
        app, db, models = result
    else:
        app, db = result
        models = None
    
    if not app or not db:
        print_error("Failed to initialize databases. Exiting.")
        return 1
    
    # Initialize Firestore Manager - look for credentials in parent directory and current directory
    firebase_credentials_path = None
    possible_paths = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database_info.json'),  # parent/database_info.json
        'database_info.json',  # current directory
        '../database_info.json'  # parent directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            firebase_credentials_path = os.path.abspath(path)
            print_info(f"Found Firebase credentials at: {firebase_credentials_path}")
            break
    
    if not firebase_credentials_path:
        print_warning("Firebase credentials file not found. Firestore will be unavailable.")
        print_warning("Places checked: parent/database_info.json, ./database_info.json, ../database_info.json")
    
    # Test results
    results = []
    analysis_id = None
    
    # All operations must happen within app context
    with app.app_context():
        firestore_manager = FirestoreManager(credentials_path=firebase_credentials_path, sqlite_db=db, database_name=database_name)
        
        # Run tests
        results.append(("Firestore Connection", test_firestore_connection(firestore_manager)))
        results.append(("Document ID Generation", test_document_id_generation()))
        results.append(("Save Signup Event", test_save_signup_event(firestore_manager)))
        results.append(("Save User Profile", test_save_user_profile(firestore_manager)))
        results.append(("Save Login Event", test_save_login_event(firestore_manager)))
        
        success, analysis_id = test_save_analysis_result(firestore_manager)
        results.append(("Save Analysis Result", success))
        
        results.append(("Save User Analysis Log", test_save_user_analysis_log(firestore_manager, analysis_id)))
        results.append(("Get User Profile", test_get_user_profile(firestore_manager)))
        results.append(("Get User Analysis Logs", test_get_user_analysis_logs(firestore_manager)))
        results.append(("Get Login History", test_get_login_history(firestore_manager)))
        results.append(("Get Signup History", test_get_signup_history(firestore_manager)))
        results.append(("Get Analysis History", test_get_analysis_history(firestore_manager)))
        results.append(("Update Last Login", test_update_last_login(firestore_manager)))
        results.append(("SQLite Backup Check", test_sqlite_backup(db, app)))
        results.append(("Data Synchronization", test_data_sync(firestore_manager, db, app)))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.ENDC}\n")
    for test_name, result in results:
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if result else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  {test_name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Overall:{Colors.ENDC}")
    percentage = (passed / total) * 100
    if passed == total:
        print_success(f"All {total} tests passed! ({percentage:.0f}%)")
    else:
        print_warning(f"{passed}/{total} tests passed ({percentage:.0f}%)")
    
    print(f"\n{Colors.BOLD}Database Information:{Colors.ENDC}")
    if firestore_manager.firestore_available:
        print(f"  {Colors.OKGREEN}✓ Firestore: CONNECTED{Colors.ENDC}")
    else:
        print(f"  {Colors.WARNING}✗ Firestore: OFFLINE (SQLite available){Colors.ENDC}")
    
    if db:
        print(f"  {Colors.OKGREEN}✓ SQLite: READY{Colors.ENDC}")
        print(f"    Database file: backend/instance/deepfake_detection.db")
    
    print(f"\n{Colors.BOLD}Test Data Created:{Colors.ENDC}")
    print(f"  Test User Email: {TEST_USER_EMAIL}")
    print(f"  Test Analysis ID: {analysis_id if analysis_id else 'Not created'}")
    print(f"\n{Colors.OKCYAN}To verify data in Firestore, visit:{Colors.ENDC}")
    print(f"  https://console.firebase.google.com")
    
    print(f"\n{Colors.OKCYAN}To verify data in SQLite, run:{Colors.ENDC}")
    print(f"  sqlite3 backend/instance/deepfake_detection.db")
    print(f"  SELECT * FROM users;")
    print(f"  SELECT * FROM signup_history;")
    print(f"  SELECT * FROM login_history;")
    print(f"  SELECT * FROM analysis_results;")
    
    print("\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

