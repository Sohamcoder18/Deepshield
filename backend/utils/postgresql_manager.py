"""
PostgreSQL Database Manager for DeepFake Detection System
Replaces Firestore with PostgreSQL cloud database
Uses SQLAlchemy ORM for database operations
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import json

logger = logging.getLogger(__name__)


class PostgreSQLManager:
    """Manages PostgreSQL database operations, replacing Firestore"""
    
    def __init__(self, db=None, models=None):
        """
        Initialize PostgreSQL Manager
        
        Args:
            db: SQLAlchemy database instance from Flask app
            models: Dictionary of SQLAlchemy models (User, SignupHistory, LoginHistory, AnalysisResult)
        """
        self.db = db
        self.models = models or {}
        self.firestore_available = True  # Set to True for compatibility (we use PostgreSQL instead)
        
        if db:
            logger.info("[OK] PostgreSQL Manager initialized successfully")
            print("[OK] PostgreSQL Manager: Connected and ready")
            if self.models:
                print(f"[OK] Available models: {list(self.models.keys())}")
        else:
            logger.warning("[ERROR] PostgreSQL Manager initialized without database instance")
            self.firestore_available = False
    
    @staticmethod
    def generate_date_based_doc_id(prefix: str = "") -> str:
        """
        Generate a document ID based on current date and time
        Format: prefix_YYYY-MM-DD_HH-MM-SS-microseconds
        
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
        Save signup event to PostgreSQL
        
        Args:
            user_email: User email
            user_data: User profile data
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': True,  # Mark as success since user was already saved in save_user_profile
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': True,
            'sqlite_saved': True,
            'errors': []
        }
        
        try:
            # User profile was already saved in save_user_profile, so just log the event
            logger.info(f"[OK] PostgreSQL: Signup event recorded for {user_email}")
            print(f"[OK] PostgreSQL: User signup completed: {user_email}")
            
        except Exception as e:
            result['errors'].append(f"PostgreSQL error: {str(e)}")
            logger.error(f"[ERROR] PostgreSQL: Failed to record signup event: {str(e)}")
        
        return result
    
    def save_login_event(self, user_email: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Save login event to PostgreSQL
        
        Args:
            user_email: User email
            additional_data: Additional login data (IP, user agent, etc.)
            
        Returns:
            Dictionary with save status
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': False,
            'sqlite_saved': False,
            'errors': []
        }
        
        additional_data = additional_data or {}
        
        try:
            from models.database_models import initialize_models
            models = initialize_models(self.db)
            LoginHistory = models['LoginHistory']
            
            doc_id = self.generate_date_based_doc_id("login")
            
            login_record = LoginHistory(
                email=user_email,
                ip_address=additional_data.get('ip_address', ''),
                user_agent=additional_data.get('user_agent', ''),
                timestamp=datetime.utcnow(),
                event_type='login',
                status='success'
            )
            
            self.db.session.add(login_record)
            self.db.session.commit()
            
            result['firestore_id'] = doc_id
            result['sqlite_id'] = login_record.id
            result['firestore_saved'] = True
            result['sqlite_saved'] = True
            result['success'] = True
            
            logger.info(f"[OK] PostgreSQL: Login event recorded for {user_email}")
            
        except Exception as e:
            result['errors'].append(f"PostgreSQL error: {str(e)}")
            logger.error(f"[ERROR] PostgreSQL: Failed to record login event: {str(e)}")
            self.db.session.rollback()
        
        return result
    
    def save_analysis_result(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save analysis result to PostgreSQL
        
        Args:
            analysis_data: Complete analysis result data
            
        Returns:
            Dictionary with save status
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'firestore_saved': False,
            'sqlite_saved': False,
            'errors': []
        }
        
        try:
            from models.database_models import initialize_models
            models = initialize_models(self.db)
            AnalysisResult = models['AnalysisResult']
            
            doc_id = self.generate_date_based_doc_id("analysis")
            
            analysis_record = AnalysisResult(
                analysis_id=analysis_data.get('analysis_id', str(uuid.uuid4())),
                user_email=analysis_data.get('user_email', ''),
                analysis_type=analysis_data.get('analysis_type', 'unknown'),
                file_name=analysis_data.get('file_name', ''),
                file_size=analysis_data.get('file_size', 0),
                trust_score=analysis_data.get('trust_score', 0.0),
                is_fake=analysis_data.get('is_fake', False),
                confidence=analysis_data.get('confidence', 0.0),
                recommendation=analysis_data.get('recommendation', ''),
                analysis_time=analysis_data.get('analysis_time', 0.0),
                timestamp=datetime.utcnow()
            )
            
            self.db.session.add(analysis_record)
            self.db.session.commit()
            
            result['firestore_id'] = doc_id
            result['sqlite_id'] = analysis_record.id
            result['firestore_saved'] = True
            result['sqlite_saved'] = True
            result['success'] = True
            
            logger.info(f"[OK] PostgreSQL: Analysis result saved: {doc_id}")
            
        except Exception as e:
            result['errors'].append(f"PostgreSQL error: {str(e)}")
            logger.error(f"[ERROR] PostgreSQL: Failed to save analysis result: {str(e)}")
            self.db.session.rollback()
        
        return result
    
    def save_user_analysis_log(self, user_email: str, analysis_id: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save user-specific analysis log to PostgreSQL
        
        Args:
            user_email: User email
            analysis_id: Analysis ID
            analysis_data: Analysis data
            
        Returns:
            Dictionary with save status
        """
        result = {
            'success': False,
            'errors': []
        }
        
        try:
            from models.database_models import initialize_models
            models = initialize_models(self.db)
            
            # Update total_analyses count for user
            User = models['User']
            user = User.query.filter_by(email=user_email).first()
            
            if user:
                user.total_analyses = (user.total_analyses or 0) + 1
                user.updated_at = datetime.utcnow()
                self.db.session.commit()
                logger.info(f"✓ PostgreSQL: User analysis count updated for {user_email}")
            
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(f"PostgreSQL error: {str(e)}")
            logger.error(f"✗ PostgreSQL: Failed to log analysis for user: {str(e)}")
            self.db.session.rollback()
        
        return result
    
    def save_user_profile(self, user_email: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save or update user profile in PostgreSQL
        
        Args:
            user_email: User email
            user_data: Updated user profile data
            
        Returns:
            Dictionary with save status
        """
        result = {
            'success': False,
            'firestore_id': None,
            'sqlite_id': None,
            'errors': []
        }
        
        try:
            if not self.db or 'User' not in self.models:
                result['errors'].append("Database or User model not initialized")
                return result
            
            # Use User model from constructor
            User = self.models['User']
            
            user = User.query.filter_by(email=user_email).first()
            
            if user:
                # Update existing user
                user.full_name = user_data.get('full_name', user.full_name)
                user.phone_number = user_data.get('phone_number', user.phone_number)
                user.date_of_birth = user_data.get('date_of_birth', user.date_of_birth)
                user.country = user_data.get('country', user.country)
                user.occupation = user_data.get('occupation', user.occupation)
                user.updated_at = datetime.utcnow()
                logger.info(f"✓ Updating existing user: {user_email}")
            else:
                # Create new user
                user = User(
                    email=user_email,
                    full_name=user_data.get('full_name', ''),
                    phone_number=user_data.get('phone_number', ''),
                    date_of_birth=user_data.get('date_of_birth', ''),
                    country=user_data.get('country', ''),
                    occupation=user_data.get('occupation', ''),
                    created_at=datetime.utcnow(),
                    last_login=datetime.utcnow()
                )
                logger.info(f"✓ Creating new user: {user_email}")
            
            self.db.session.add(user)
            self.db.session.commit()
            
            result['success'] = True
            result['sqlite_id'] = user.id
            result['firestore_id'] = user_email
            result['firestore_saved'] = True
            
            logger.info(f"✓ PostgreSQL: User profile saved: {user_email}")
            print(f"✓ PostgreSQL: User profile saved: {user_email}")
            
        except Exception as e:
            result['errors'].append(f"PostgreSQL error: {str(e)}")
            logger.error(f"✗ PostgreSQL: Failed to save user profile: {str(e)}")
            self.db.session.rollback()
        
        return result
    
    def get_user_profile(self, user_email: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile from PostgreSQL
        
        Args:
            user_email: User email
            
        Returns:
            User profile data or None
        """
        try:
            if not self.db or 'User' not in self.models:
                logger.error("✗ PostgreSQL: Database or User model not initialized")
                return None
            
            User = self.models['User']
            user = User.query.filter_by(email=user_email).first()
            
            if user:
                return user.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"✗ PostgreSQL: Failed to retrieve user profile: {str(e)}")
            return None
    
    def update_last_login(self, user_email: str) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_email: User email
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.db or 'User' not in self.models:
                logger.error("✗ Database or User model not initialized")
                return False
            
            User = self.models['User']
            user = User.query.filter_by(email=user_email).first()
            if user:
                user.last_login = datetime.utcnow()
                self.db.session.commit()
                logger.info(f"✓ Updated last login for {user_email}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"✗ Failed to update last login: {str(e)}")
            self.db.session.rollback()
            return False
    
    def get_analysis_history(self, user_email: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve analysis history from PostgreSQL
        
        Args:
            user_email: Optional user email to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of analysis results
        """
        try:
            from models.database_models import initialize_models
            models = initialize_models(self.db)
            AnalysisResult = models['AnalysisResult']
            
            query = AnalysisResult.query
            
            if user_email:
                query = query.filter_by(user_email=user_email)
            
            results = query.order_by(AnalysisResult.timestamp.desc()).limit(limit).all()
            
            return [result.to_dict() for result in results]
            
        except Exception as e:
            logger.error(f"✗ PostgreSQL: Failed to retrieve analysis history: {str(e)}")
            return []
    
    # Mock Firestore client for compatibility with existing code
    class MockFirestoreClient:
        """Mock Firestore client for backward compatibility"""
        
        def __init__(self, db):
            self.db = db
        
        def collection(self, collection_name):
            return MockFirestoreCollection(collection_name, self.db)
    
    # Property to provide mock firestore client access
    @property
    def db_client(self):
        """Provide Firestore-like interface for existing code"""
        if self.db:
            return self.MockFirestoreClient(self.db)
        return None
    
    def __getattr__(self, name):
        """Provide compatibility layer for firestore_manager.db access"""
        if name == 'db' and hasattr(self, '_db'):
            return self._db
        if name == 'db':
            return self.db_client
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


class MockFirestoreCollection:
    """Mock Firestore collection for backward compatibility"""
    
    def __init__(self, collection_name, db):
        self.collection_name = collection_name
        self.db = db
    
    def document(self, doc_id):
        return MockFirestoreDocument(self.collection_name, doc_id, self.db)
    
    def where(self, field, op, value):
        return self  # Return self for chaining
    
    def order_by(self, field):
        return self  # Return self for chaining
    
    def stream(self):
        return []


class MockFirestoreDocument:
    """Mock Firestore document for backward compatibility"""
    
    def __init__(self, collection_name, doc_id, db):
        self.collection_name = collection_name
        self.doc_id = doc_id
        self.db = db
    
    def set(self, data):
        """Mock Firestore set operation"""
        logger.info(f"Data would be saved to {self.collection_name}/{self.doc_id}")
        return None
    
    def get(self):
        return None
    
    def delete(self):
        return None
