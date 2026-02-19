"""
Firestore Database Utility Functions for DeepFake Detection System
Handles Firestore operations with SQLite backup
Uses date-based document IDs for better organization and tracking
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid
import os
import json
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


class FirestoreManager:
    """Manages Firestore operations with SQLite backup"""
    
    def __init__(self, credentials_path: str = None, sqlite_db=None, database_name: str = None):
        """
        Initialize FirestoreManager
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            sqlite_db: SQLAlchemy database instance for backup
            database_name: Name of Firestore database to connect to (default: None uses 'default')
        """
        self.sqlite_db = sqlite_db
        self.db = None
        self.firestore_available = False
        self.cred = None
        self.database_name = database_name or os.getenv('FIRESTORE_DATABASE', 'default')
        
        # Initialize Firestore
        try:
            # Try to get credentials from environment variable first
            creds_json = os.getenv('FIREBASE_CREDENTIALS_JSON', '')
            
            if creds_json:
                creds_dict = json.loads(creds_json)
                self.cred = credentials.Certificate(creds_dict)
            elif credentials_path and os.path.exists(credentials_path):
                self.cred = credentials.Certificate(credentials_path)
            else:
                # Try default location
                default_path = 'database_info.json'
                if os.path.exists(default_path):
                    self.cred = credentials.Certificate(default_path)
            
            if self.cred:
                # Initialize Firebase app (only once, with explicit project ID)
                try:
                    app = firebase_admin.get_app()
                except ValueError:
                    # Get project ID from credentials
                    cred_data = self.cred.certificate if hasattr(self.cred, 'certificate') else {}
                    project_id = cred_data.get('project_id', 'deepfake-5e76b')
                    app = firebase_admin.initialize_app(self.cred, {'projectId': project_id})
                
                # Connect to Firestore with explicit database parameter
                try:
                    # Try with explicit database parameter (newer versions)
                    self.db = firestore.client(database=self.database_name)
                except TypeError:
                    # Fallback for older versions without database parameter
                    self.db = firestore.client()
                
                # Test connection capability (but don't fail silently for billing issues)
                try:
                    # Try a simple collection list to validate access
                    list(self.db.collections())
                    self.firestore_available = True
                    logger.info(f"✓ Connected to Firestore database '{self.database_name}' successfully")
                    print(f"✓ Firestore Connection: SUCCESS - Database: '{self.database_name}'")
                except Exception as firestore_error:
                    # Firestore not available, will use SQLite only
                    self.firestore_available = False
                    logger.info(f"⚠ Firestore unavailable, using SQLite only: {str(firestore_error)[:100]}")
                    print(f"⚠ Firestore unavailable (billing/permissions issue)")
                    print(f"✓ Using SQLite database for all operations")
            else:
                logger.warning("✗ Firebase credentials not found")
                print("ℹ  Firestore not configured - Using SQLite only")
                self.firestore_available = False
        except Exception as e:
            # Firestore initialization failed, use SQLite only
            self.firestore_available = False
            logger.info(f"ℹ SQLite-only mode: Firestore unavailable ({type(e).__name__})")
            print(f"✓ Using SQLite database for all operations")
            self.firestore_available = False
    
    def create_collections(self) -> bool:
        """
        Initialize required Firestore collections with indexes
        Creates collections: users, signup_history, login_history, analysis_results
        
        Returns:
            True if successful, False otherwise
        """
        if not self.firestore_available:
            logger.warning("Cannot create collections - Firestore not available")
            return False
        
        try:
            collections = {
                'users': {'email': 'test@example.com', '_created': datetime.utcnow().isoformat()},
                'signup_history': {'email': 'test@example.com', '_created': datetime.utcnow().isoformat()},
                'login_history': {'email': 'test@example.com', '_created': datetime.utcnow().isoformat()},
                'analysis_results': {'user_email': 'test@example.com', '_created': datetime.utcnow().isoformat()}
            }
            
            for collection_name, initial_doc in collections.items():
                try:
                    # Create collection by adding a dummy document then deleting it
                    self.db.collection(collection_name).document('_init_').set(initial_doc)
                    self.db.collection(collection_name).document('_init_').delete()
                    logger.info(f"✓ Collection initialized: {collection_name}")
                    print(f"✓ Collection initialized: {collection_name}")
                except Exception as col_err:
                    logger.warning(f"Warning initializing {collection_name}: {str(col_err)}")
            
            print("✓ All required Firestore collections have been initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to create collections: {str(e)}")
            print(f"✗ Failed to initialize collections: {str(e)}")
            return False
    
    @staticmethod
    def generate_date_based_doc_id(prefix: str = "") -> str:
        """
        Generate a document ID based on current date and time
        Format: prefix_YYYY-MM-DD_HH-MM-SS-microseconds
        This allows developers to quickly understand when events occurred
        
        Args:
            prefix: Optional prefix for the document ID
            
        Returns:
            Generated document ID string
        """
        now = datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        microseconds = str(now.microsecond).zfill(6)
        unique_id = str(uuid.uuid4())[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}"
        return f"{timestamp}_{microseconds}_{unique_id}"
    
    def save_signup_event(self, user_email: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save signup event to separate field/collection (PRIMARY: Firestore, BACKUP: SQLite)
        Document ID format: signup_YYYY-MM-DD_HH-MM-SS-uid
        
        Args:
            user_email: User email
            user_data: User profile data
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': False,
            'sqlite_saved': False,
            'errors': []
        }
        
        doc_id = self.generate_date_based_doc_id("signup")
        signup_data = {
            'email': user_email,
            'full_name': user_data.get('full_name', ''),
            'phone_number': user_data.get('phone_number', ''),
            'date_of_birth': user_data.get('date_of_birth', ''),
            'country': user_data.get('country', ''),
            'occupation': user_data.get('occupation', ''),
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'signup',
            'status': 'success'
        }
        
        # Save to Firestore (PRIMARY)
        if self.firestore_available:
            try:
                self.db.collection('signup_history').document(doc_id).set(signup_data)
                result['firestore_id'] = doc_id
                result['firestore_saved'] = True
                result['success'] = True
                logger.info(f"✓ FIRESTORE: Signup event recorded: {doc_id}")
                print(f"✓ FIRESTORE: Signup event saved: {user_email}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"✗ FIRESTORE: Failed to record signup event: {str(e)}")
                print(f"✗ FIRESTORE: Failed to record signup: {str(e)}")
        else:
            logger.warning("⚠ FIRESTORE: Not available for signup event")
        
        # Save to SQLite as Backup
        if self.sqlite_db is not None:
            try:
                self.sqlite_db.session.execute(
                    text("""INSERT INTO signup_history (email, full_name, phone_number, date_of_birth, country, occupation, timestamp, event_type, status)
                            VALUES (:email, :full_name, :phone_number, :date_of_birth, :country, :occupation, :timestamp, 'signup', 'success')"""),
                    {
                        'email': user_email,
                        'full_name': user_data.get('full_name', ''),
                        'phone_number': user_data.get('phone_number', ''),
                        'date_of_birth': user_data.get('date_of_birth', ''),
                        'country': user_data.get('country', ''),
                        'occupation': user_data.get('occupation', ''),
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                self.sqlite_db.session.commit()
                result['sqlite_saved'] = True
                if not result['success']:
                    result['success'] = True
                logger.info(f"✓ SQLITE: Signup event backed up: {user_email}")
                print(f"✓ SQLITE: Signup event backed up: {user_email}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"✗ SQLITE: Failed to backup signup event: {str(e)}")
                print(f"✗ SQLITE: Failed to backup signup: {str(e)}")
        
        # Log final status
        if result['firestore_saved']:
            logger.info(f"[SIGNUP] ✓ PRIMARY (Firestore) - Event recorded")
        elif result['sqlite_saved']:
            logger.warning(f"[SIGNUP] ⚠ BACKUP ONLY (SQLite) - Firestore unavailable")
        else:
            logger.error(f"[SIGNUP] ✗ FAILED - Could not save signup event to any database")
        
        
        return result
    
    def save_login_event(self, user_email: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save login event to separate field/collection (PRIMARY: Firestore, BACKUP: SQLite)
        Document ID format: login_YYYY-MM-DD_HH-MM-SS-uid
        
        Args:
            user_email: User email
            additional_data: Optional additional data (IP, user agent, etc.)
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': False,
            'sqlite_saved': False,
            'errors': []
        }
        
        doc_id = self.generate_date_based_doc_id("login")
        login_data = {
            'email': user_email,
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': 'login',
            'status': 'success'
        }
        
        if additional_data:
            login_data.update(additional_data)
        
        # Save to Firestore (PRIMARY)
        if self.firestore_available:
            try:
                self.db.collection('login_history').document(doc_id).set(login_data)
                result['firestore_id'] = doc_id
                result['firestore_saved'] = True
                result['success'] = True
                logger.info(f"✓ FIRESTORE: Login event recorded: {doc_id}")
                print(f"✓ FIRESTORE: Login event saved: {user_email}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"✗ FIRESTORE: Failed to record login event: {str(e)}")
                print(f"✗ FIRESTORE: Failed to record login: {str(e)}")
        else:
            logger.warning("⚠ FIRESTORE: Not available for login event")
        
        # Save to SQLite as Backup
        if self.sqlite_db is not None:
            try:
                self.sqlite_db.session.execute(
                    text("""INSERT INTO login_history (email, ip_address, user_agent, timestamp, event_type, status)
                            VALUES (:email, :ip_address, :user_agent, :timestamp, 'login', 'success')"""),
                    {
                        'email': user_email,
                        'ip_address': additional_data.get('ip_address', '') if additional_data else '',
                        'user_agent': additional_data.get('user_agent', '') if additional_data else '',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )
                self.sqlite_db.session.commit()
                result['sqlite_saved'] = True
                if not result['success']:
                    result['success'] = True
                logger.info(f"✓ SQLITE: Login event backed up: {user_email}")
                print(f"✓ SQLITE: Login event backed up: {user_email}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"✗ SQLITE: Failed to backup login event: {str(e)}")
                print(f"✗ SQLITE: Failed to backup login: {str(e)}")
        
        # Log final status
        if result['firestore_saved']:
            logger.info(f"[LOGIN] ✓ PRIMARY (Firestore) - Event recorded")
        elif result['sqlite_saved']:
            logger.warning(f"[LOGIN] ⚠ BACKUP ONLY (SQLite) - Firestore unavailable")
        else:
            logger.error(f"[LOGIN] ✗ FAILED - Could not save login event to any database")
        
        return result
    
    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save analysis result to separate collection
        Document ID format: analysis_YYYY-MM-DD_HH-MM-SS-uid
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'errors': []
        }
        
        doc_id = self.generate_date_based_doc_id("analysis")
        user_email = analysis_data.get('user_email', '')
        
        if 'timestamp' not in analysis_data:
            analysis_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Save to Firestore
        if self.firestore_available:
            try:
                self.db.collection('analysis_results').document(doc_id).set(analysis_data)
                result['firestore_id'] = doc_id
                result['success'] = True
                logger.info(f"Analysis result saved to Firestore: {doc_id}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"Failed to save analysis to Firestore: {str(e)}")
        
        # Save to SQLite as backup
        if self.sqlite_db is not None:
            try:
                # Use raw SQL to avoid circular imports and model initialization issues
                self.sqlite_db.session.execute(
                    text("""INSERT INTO analysis_results (analysis_id, user_email, analysis_type, file_name, file_size, trust_score, is_fake, confidence, recommendation, analysis_time, timestamp, metadata)
                            VALUES (:analysis_id, :user_email, :analysis_type, :file_name, :file_size, :trust_score, :is_fake, :confidence, :recommendation, :analysis_time, :timestamp, :metadata)"""),
                    {
                        'analysis_id': doc_id,
                        'user_email': user_email,
                        'analysis_type': analysis_data.get('analysis_type', ''),
                        'file_name': analysis_data.get('file_name', ''),
                        'file_size': analysis_data.get('file_size', 0),
                        'trust_score': analysis_data.get('trust_score', 0),
                        'is_fake': analysis_data.get('is_fake', False),
                        'confidence': analysis_data.get('confidence', 0),
                        'recommendation': analysis_data.get('recommendation', ''),
                        'analysis_time': analysis_data.get('analysis_time', 0),
                        'timestamp': datetime.utcnow().isoformat(),
                        'metadata': json.dumps(analysis_data.get('metadata', {}))
                    }
                )
                self.sqlite_db.session.commit()
                logger.info(f"Analysis result saved to SQLite backup")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"Failed to save analysis to SQLite: {str(e)}")
        
        # Increment user's analysis count
        if user_email and result['success']:
            self.increment_user_analysis_count(user_email)
        
        return result
    
    def save_user_analysis_log(self, user_email: str, analysis_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save to user-specific analysis log
        This creates a subcollection under user document for tracking all analyses by a user
        
        Args:
            user_email: User email
            analysis_id: Analysis ID
            analysis_data: Analysis details
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'firestore_id': None,
            'errors': []
        }
        
        doc_id = self.generate_date_based_doc_id("anl")
        
        log_entry = {
            'analysis_id': analysis_id,
            'analysis_type': analysis_data.get('analysis_type', ''),
            'file_name': analysis_data.get('file_name', ''),
            'is_fake': analysis_data.get('is_fake', False),
            'confidence': analysis_data.get('confidence', 0),
            'trust_score': analysis_data.get('trust_score', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to Firestore under user's analysis logs subcollection
        if self.firestore_available:
            try:
                self.db.collection('users').document(user_email).collection('analysis_logs').document(doc_id).set(log_entry)
                result['firestore_id'] = doc_id
                result['success'] = True
                logger.info(f"User analysis log saved to Firestore: {user_email}/{doc_id}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"Failed to save user analysis log to Firestore: {str(e)}")
        
        return result
    
    def save_user_profile(self, user_email: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save/update user profile in Firestore users collection (PRIMARY)
        Falls back to SQLite if Firestore unavailable
        
        Args:
            user_email: User email (used as document ID)
            user_data: User profile data
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': False,
            'sqlite_saved': False,
            'errors': []
        }
        
        # Convert datetime objects to ISO format strings for Firestore
        created_at = user_data.get('created_at')
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        else:
            created_at = created_at or datetime.utcnow().isoformat()
        
        profile_data = {
            'email': user_email,
            'full_name': user_data.get('full_name', ''),
            'phone_number': user_data.get('phone_number', ''),
            'date_of_birth': user_data.get('date_of_birth', ''),
            'country': user_data.get('country', ''),
            'occupation': user_data.get('occupation', ''),
            'created_at': created_at,
            'last_login': datetime.utcnow().isoformat(),
            'total_analyses': user_data.get('total_analyses', 0),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save to Firestore (PRIMARY)
        if self.firestore_available:
            try:
                self.db.collection('users').document(user_email).set(profile_data, merge=True)
                result['firestore_id'] = user_email
                result['firestore_saved'] = True
                result['success'] = True  # Mark success if Firestore saves
                logger.info(f"✓ FIRESTORE: User profile saved successfully: {user_email}")
                print(f"✓ FIRESTORE: User profile saved: {user_email}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"✗ FIRESTORE: Failed to save user profile: {str(e)}")
                print(f"✗ FIRESTORE: Failed to save user profile: {str(e)}")
        else:
            logger.warning("⚠ FIRESTORE: Not available - using SQLite only")
            print("⚠ FIRESTORE: Database not available")
        
        # Save to SQLite as Backup
        if self.sqlite_db is not None:
            try:
                # Check if user already exists
                existing = self.sqlite_db.session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": user_email}
                ).fetchone()
                
                if existing:
                    # Update existing user
                    self.sqlite_db.session.execute(
                        text("""UPDATE users 
                                SET full_name = :full_name, 
                                    phone_number = :phone_number, 
                                    date_of_birth = :date_of_birth,
                                    country = :country,
                                    occupation = :occupation,
                                    last_login = :last_login,
                                    updated_at = :updated_at
                                WHERE email = :email"""),
                        {
                            'email': user_email,
                            'full_name': user_data.get('full_name', ''),
                            'phone_number': user_data.get('phone_number', ''),
                            'date_of_birth': user_data.get('date_of_birth', ''),
                            'country': user_data.get('country', ''),
                            'occupation': user_data.get('occupation', ''),
                            'last_login': datetime.utcnow().isoformat(),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    )
                else:
                    # Insert new user
                    self.sqlite_db.session.execute(
                        text("""INSERT INTO users (email, full_name, phone_number, date_of_birth, country, occupation, created_at, last_login, total_analyses, updated_at)
                                VALUES (:email, :full_name, :phone_number, :date_of_birth, :country, :occupation, :created_at, :last_login, 0, :updated_at)"""),
                        {
                            'email': user_email,
                            'full_name': user_data.get('full_name', ''),
                            'phone_number': user_data.get('phone_number', ''),
                            'date_of_birth': user_data.get('date_of_birth', ''),
                            'country': user_data.get('country', ''),
                            'occupation': user_data.get('occupation', ''),
                            'created_at': created_at,
                            'last_login': datetime.utcnow().isoformat(),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    )
                
                self.sqlite_db.session.commit()
                result['sqlite_id'] = user_email
                result['sqlite_saved'] = True
                # Mark as success if SQLite saves (even if Firestore failed)
                if not result['success']:
                    result['success'] = True
                logger.info(f"✓ SQLITE: User profile saved to backup: {user_email}")
                print(f"✓ SQLITE: User profile backed up: {user_email}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"✗ SQLITE: Failed to save user profile: {str(e)}")
                print(f"✗ SQLITE: Failed to save user profile: {str(e)}")
        
        # Log final status
        if result['firestore_saved']:
            logger.info(f"[PROFILE] ✓ PRIMARY (Firestore) - User profile saved")
        elif result['sqlite_saved']:
            logger.warning(f"[PROFILE] ⚠ BACKUP ONLY (SQLite) - Firestore unavailable, using SQLite")
        else:
            logger.error(f"[PROFILE] ✗ FAILED - Could not save to either database")
        
        return result
    
    def get_user_profile(self, user_email: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile from Firestore or SQLite
        
        Args:
            user_email: User email
            
        Returns:
            User profile dictionary or None
        """
        # Try Firestore first
        if self.firestore_available:
            try:
                doc = self.db.collection('users').document(user_email).get()
                if doc.exists:
                    return doc.to_dict()
            except Exception as e:
                logger.warning(f"Failed to get user from Firestore: {str(e)}")
        
        # Fallback to SQLite
        if self.sqlite_db is not None:
            try:
                # Query directly without importing model to avoid circular imports
                user_row = self.sqlite_db.session.execute(
                    text("SELECT email, full_name, phone_number, date_of_birth, country, occupation, created_at, last_login, total_analyses FROM users WHERE email = :email"),
                    {"email": user_email}
                ).fetchone()
                
                if user_row:
                    return {
                        'email': user_row[0],
                        'full_name': user_row[1] or '',
                        'phone_number': user_row[2] or '',
                        'date_of_birth': user_row[3] or '',
                        'country': user_row[4] or '',
                        'occupation': user_row[5] or '',
                        'created_at': user_row[6],
                        'last_login': user_row[7],
                        'total_analyses': user_row[8] or 0
                    }
            except Exception as e:
                logger.warning(f"Failed to get user from SQLite: {str(e)}")
    
    def get_user_analysis_logs(self, user_email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's analysis logs
        
        Args:
            user_email: User email
            limit: Maximum number of logs to retrieve
            
        Returns:
            List of analysis logs
        """
        logs = []
        
        # Try Firestore first
        if self.firestore_available:
            try:
                docs = self.db.collection('users').document(user_email).collection('analysis_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
                for doc in docs:
                    log_data = doc.to_dict()
                    log_data['_id'] = doc.id
                    logs.append(log_data)
                return logs
            except Exception as e:
                logger.warning(f"Failed to get analysis logs from Firestore: {str(e)}")
        
        # Fallback to SQLite
        if self.sqlite_db is not None:
            try:
                # Query directly without importing model to avoid circular imports
                results = self.sqlite_db.session.execute(
                    text("""SELECT id, user_email, analysis_type, is_fake, confidence, timestamp, metadata 
                            FROM analysis_results 
                            WHERE user_email = :user_email 
                            ORDER BY timestamp DESC 
                            LIMIT :limit"""),
                    {"user_email": user_email, "limit": limit}
                ).fetchall()
                
                logs = []
                for row in results:
                    log_dict = {
                        'id': row[0],
                        'user_email': row[1],
                        'analysis_type': row[2],
                        'is_fake': row[3],
                        'confidence': row[4],
                        'timestamp': row[5],
                        'metadata': row[6]
                    }
                    logs.append(log_dict)
            except Exception as e:
                logger.warning(f"Failed to get analysis logs from SQLite: {str(e)}")
        
        return logs
    
    def update_last_login(self, user_email: str) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_email: User email
            
        Returns:
            Success status
        """
        now = datetime.utcnow().isoformat()
        
        # Update Firestore
        if self.firestore_available:
            try:
                self.db.collection('users').document(user_email).update({
                    'last_login': now,
                    'updated_at': now
                })
                logger.info(f"Updated last login for {user_email} in Firestore")
            except Exception as e:
                logger.error(f"Failed to update last login in Firestore: {str(e)}")
        
        # Update SQLite
        if self.sqlite_db is not None:
            try:
                # Use raw SQL to avoid model imports
                self.sqlite_db.session.execute(
                    text("""UPDATE users 
                            SET last_login = :last_login, updated_at = :updated_at
                            WHERE email = :email"""),
                    {
                        'email': user_email,
                        'last_login': now,
                        'updated_at': now
                    }
                )
                self.sqlite_db.session.commit()
                logger.info(f"Updated last login for {user_email} in SQLite")
            except Exception as e:
                logger.error(f"Failed to update last login in SQLite: {str(e)}")
                self.sqlite_db.session.rollback()
                logger.error(f"Failed to update last login in SQLite: {str(e)}")
        
        return True
    
    def get_login_history(self, user_email: str = None, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get login history (across all users or specific user)
        
        Args:
            user_email: Optional email to filter by specific user
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of login history records
        """
        logs = []
        
        if self.firestore_available:
            try:
                query = self.db.collection('login_history')
                
                if user_email:
                    query = query.where('email', '==', user_email)
                
                docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
                
                for doc in docs:
                    log_data = doc.to_dict()
                    log_data['_id'] = doc.id
                    logs.append(log_data)
            except Exception as e:
                logger.warning(f"Failed to get login history from Firestore: {str(e)}")
        
        return logs
    
    def get_signup_history(self, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get signup history
        
        Args:
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of signup history records
        """
        logs = []
        
        if self.firestore_available:
            try:
                docs = self.db.collection('signup_history').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
                
                for doc in docs:
                    log_data = doc.to_dict()
                    log_data['_id'] = doc.id
                    logs.append(log_data)
            except Exception as e:
                logger.warning(f"Failed to get signup history from Firestore: {str(e)}")
        
        return logs
    
    def get_analysis_history(self, user_email: str = None, days: int = 30, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analysis history
        
        Args:
            user_email: Optional email to filter by specific user
            days: Number of days to look back
            limit: Maximum number of records
            
        Returns:
            List of analysis records
        """
        logs = []
        
        if self.firestore_available:
            try:
                query = self.db.collection('analysis_results')
                
                if user_email:
                    query = query.where('user_email', '==', user_email)
                
                docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
                
                for doc in docs:
                    log_data = doc.to_dict()
                    log_data['_id'] = doc.id
                    logs.append(log_data)
            except Exception as e:
                logger.warning(f"Failed to get analysis history from Firestore: {str(e)}")
        
        return logs
    
    def increment_user_analysis_count(self, user_email: str) -> bool:
        """
        Increment the total_analyses counter for a user
        
        Args:
            user_email: User email
            
        Returns:
            True if successful, False otherwise
        """
        if not user_email or self.sqlite_db is None:
            return False
        
        try:
            # Update SQLite: increment total_analyses
            self.sqlite_db.session.execute(
                text("""UPDATE users SET total_analyses = total_analyses + 1 WHERE email = :email"""),
                {'email': user_email}
            )
            self.sqlite_db.session.commit()
            logger.info(f"✓ Analysis count incremented for user: {user_email}")
            return True
        except Exception as e:
            self.sqlite_db.session.rollback()
            logger.error(f"✗ Failed to increment analysis count: {str(e)}")
            return False
