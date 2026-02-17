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
                # Initialize Firebase app (only once)
                try:
                    firebase_admin.get_app()
                except ValueError:
                    firebase_admin.initialize_app(self.cred)
                
                # Connect to Firestore with specified database
                # Use database_id parameter (not 'database')
                self.db = firestore.client(database_id=self.database_name)
                self.firestore_available = True
                logger.info(f"✓ Connected to Firestore database '{self.database_name}' successfully")
                print(f"✓ Firestore Connection: SUCCESS - Database: '{self.database_name}'")
            else:
                logger.warning("✗ Firebase credentials not found")
                print("ℹ  Firestore not configured - Falling back to SQLite")
        except Exception as e:
            logger.warning(f"Firestore connection unavailable: {type(e).__name__}: {str(e)}")
            print(f"ℹ  Firestore unavailable ({type(e).__name__}) - Using SQLite for backup storage")
            self.firestore_available = False
    
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
        Save signup event to separate field/collection
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
        
        # Save to Firestore
        if self.firestore_available:
            try:
                self.db.collection('signup_history').document(doc_id).set(signup_data)
                result['firestore_id'] = doc_id
                result['success'] = True
                logger.info(f"Signup event saved to Firestore: {doc_id}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"Failed to save signup to Firestore: {str(e)}")
        
        # Save to SQLite as backup
        if self.sqlite_db is not None:
            try:
                from models.database_models import SignupHistory
                signup_record = SignupHistory(
                    email=user_email,
                    full_name=user_data.get('full_name', ''),
                    phone_number=user_data.get('phone_number', ''),
                    date_of_birth=user_data.get('date_of_birth', ''),
                    country=user_data.get('country', ''),
                    occupation=user_data.get('occupation', ''),
                    timestamp=datetime.utcnow()
                )
                self.sqlite_db.session.add(signup_record)
                self.sqlite_db.session.commit()
                result['sqlite_id'] = signup_record.id
                logger.info(f"Signup event saved to SQLite backup: {signup_record.id}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"Failed to save signup to SQLite: {str(e)}")
        
        return result
    
    def save_login_event(self, user_email: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save login event to separate field/collection
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
        
        # Save to Firestore
        if self.firestore_available:
            try:
                self.db.collection('login_history').document(doc_id).set(login_data)
                result['firestore_id'] = doc_id
                result['success'] = True
                logger.info(f"Login event saved to Firestore: {doc_id}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"Failed to save login to Firestore: {str(e)}")
        
        # Save to SQLite as backup
        if self.sqlite_db is not None:
            try:
                from models.database_models import LoginHistory
                login_record = LoginHistory(
                    email=user_email,
                    ip_address=additional_data.get('ip_address', '') if additional_data else '',
                    user_agent=additional_data.get('user_agent', '') if additional_data else '',
                    timestamp=datetime.utcnow()
                )
                self.sqlite_db.session.add(login_record)
                self.sqlite_db.session.commit()
                result['sqlite_id'] = login_record.id
                logger.info(f"Login event saved to SQLite backup: {login_record.id}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"Failed to save login to SQLite: {str(e)}")
        
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
                from models.database_models import AnalysisResult
                analysis_record = AnalysisResult(
                    analysis_id=doc_id,
                    user_email=analysis_data.get('user_email', ''),
                    analysis_type=analysis_data.get('analysis_type', ''),
                    file_name=analysis_data.get('file_name', ''),
                    file_size=analysis_data.get('file_size', 0),
                    trust_score=analysis_data.get('trust_score', 0),
                    is_fake=analysis_data.get('is_fake', False),
                    confidence=analysis_data.get('confidence', 0),
                    recommendation=analysis_data.get('recommendation', ''),
                    analysis_time=analysis_data.get('analysis_time', 0),
                    timestamp=datetime.utcnow()
                )
                self.sqlite_db.session.add(analysis_record)
                self.sqlite_db.session.commit()
                result['sqlite_id'] = analysis_record.id
                logger.info(f"Analysis result saved to SQLite backup: {analysis_record.id}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"Failed to save analysis to SQLite: {str(e)}")
        
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
        Save/update user profile in Firestore users collection
        
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
            'errors': []
        }
        
        profile_data = {
            'email': user_email,
            'full_name': user_data.get('full_name', ''),
            'phone_number': user_data.get('phone_number', ''),
            'date_of_birth': user_data.get('date_of_birth', ''),
            'country': user_data.get('country', ''),
            'occupation': user_data.get('occupation', ''),
            'created_at': user_data.get('created_at', datetime.utcnow().isoformat()),
            'last_login': datetime.utcnow().isoformat(),
            'total_analyses': user_data.get('total_analyses', 0),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Save to Firestore
        if self.firestore_available:
            try:
                # Use set with merge=True to update or create
                self.db.collection('users').document(user_email).set(profile_data, merge=True)
                result['firestore_id'] = user_email
                result['success'] = True
                logger.info(f"User profile saved to Firestore: {user_email}")
            except Exception as e:
                result['errors'].append(f"Firestore error: {str(e)}")
                logger.error(f"Failed to save user profile to Firestore: {str(e)}")
        
        # Save to SQLite as backup
        if self.sqlite_db is not None:
            try:
                from models.database_models import User
                existing_user = User.query.filter_by(email=user_email).first()
                
                if existing_user:
                    existing_user.full_name = user_data.get('full_name', existing_user.full_name)
                    existing_user.phone_number = user_data.get('phone_number', existing_user.phone_number)
                    existing_user.date_of_birth = user_data.get('date_of_birth', existing_user.date_of_birth)
                    existing_user.country = user_data.get('country', existing_user.country)
                    existing_user.occupation = user_data.get('occupation', existing_user.occupation)
                    existing_user.last_login = datetime.utcnow()
                    existing_user.updated_at = datetime.utcnow()
                else:
                    new_user = User(
                        email=user_email,
                        full_name=user_data.get('full_name', ''),
                        phone_number=user_data.get('phone_number', ''),
                        date_of_birth=user_data.get('date_of_birth', ''),
                        country=user_data.get('country', ''),
                        occupation=user_data.get('occupation', ''),
                        created_at=datetime.utcnow(),
                        last_login=datetime.utcnow(),
                        total_analyses=0
                    )
                    self.sqlite_db.session.add(new_user)
                
                self.sqlite_db.session.commit()
                result['sqlite_id'] = user_email
                logger.info(f"User profile saved to SQLite backup: {user_email}")
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
                logger.error(f"Failed to save user profile to SQLite: {str(e)}")
        
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
                from models.database_models import User
                user = User.query.filter_by(email=user_email).first()
                if user:
                    return user.to_dict()
            except Exception as e:
                logger.warning(f"Failed to get user from SQLite: {str(e)}")
        
        return None
    
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
                from models.database_models import AnalysisResult
                results = AnalysisResult.query.filter_by(user_email=user_email).order_by(AnalysisResult.timestamp.desc()).limit(limit).all()
                logs = [r.to_dict() for r in results]
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
                from models.database_models import User
                user = User.query.filter_by(email=user_email).first()
                if user:
                    user.last_login = datetime.utcnow()
                    user.updated_at = datetime.utcnow()
                    self.sqlite_db.session.commit()
                    logger.info(f"Updated last login for {user_email} in SQLite")
            except Exception as e:
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
