"""
Database Models for DeepFake Detection System
Supports Firestore with SQLite backup
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text

# Global db instance will be set by Flask app
db = None

# Global model classes (set after initialization)
User = None
SignupHistory = None
LoginHistory = None
AnalysisResult = None

def initialize_models(flask_db):
    """Initialize models with Flask-SQLAlchemy instance"""
    global db, User, SignupHistory, LoginHistory, AnalysisResult
    
    if User is not None:
        return {
            'User': User,
            'SignupHistory': SignupHistory,
            'LoginHistory': LoginHistory,
            'AnalysisResult': AnalysisResult
        }
        
    db = flask_db
    
    class UserModel(db.Model):
        """SQLite model for storing user profile information"""
        __tablename__ = 'users'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        email = Column(String(120), unique=True, nullable=False, index=True)
        full_name = Column(String(120), nullable=True)
        phone_number = Column(String(20), nullable=True)
        date_of_birth = Column(String(20), nullable=True)
        country = Column(String(50), nullable=True)
        occupation = Column(String(100), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        last_login = Column(DateTime, default=datetime.utcnow)
        total_analyses = Column(Integer, default=0)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'full_name': self.full_name or '',
                'phone_number': self.phone_number or '',
                'date_of_birth': self.date_of_birth or '',
                'country': self.country or '',
                'occupation': self.occupation or '',
                'created_at': self.created_at.isoformat() if self.created_at else '',
                'last_login': self.last_login.isoformat() if self.last_login else '',
                'total_analyses': self.total_analyses or 0,
                'updated_at': self.updated_at.isoformat() if self.updated_at else ''
            }
    
    class SignupHistoryModel(db.Model):
        """SQLite model for tracking signup events (Firestore backup)"""
        __tablename__ = 'signup_history'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        email = Column(String(120), nullable=False, index=True)
        full_name = Column(String(120), nullable=True)
        phone_number = Column(String(20), nullable=True)
        date_of_birth = Column(String(20), nullable=True)
        country = Column(String(50), nullable=True)
        occupation = Column(String(100), nullable=True)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        event_type = Column(String(20), default='signup')
        status = Column(String(20), default='success')
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'full_name': self.full_name or '',
                'phone_number': self.phone_number or '',
                'date_of_birth': self.date_of_birth or '',
                'country': self.country or '',
                'occupation': self.occupation or '',
                'timestamp': self.timestamp.isoformat() if self.timestamp else '',
                'event_type': self.event_type,
                'status': self.status
            }
    
    class LoginHistoryModel(db.Model):
        """SQLite model for tracking login events (Firestore backup)"""
        __tablename__ = 'login_history'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        email = Column(String(120), nullable=False, index=True)
        ip_address = Column(String(50), nullable=True)
        user_agent = Column(String(500), nullable=True)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        event_type = Column(String(20), default='login')
        status = Column(String(20), default='success')
        
        def to_dict(self):
            return {
                'id': self.id,
                'email': self.email,
                'ip_address': self.ip_address or '',
                'user_agent': self.user_agent or '',
                'timestamp': self.timestamp.isoformat() if self.timestamp else '',
                'event_type': self.event_type,
                'status': self.status
            }
    
    class AnalysisResultModel(db.Model):
        """SQLite model for storing analysis results (Firestore backup)"""
        __tablename__ = 'analysis_results'
        __table_args__ = {'extend_existing': True}
        
        id = Column(Integer, primary_key=True)
        analysis_id = Column(String(100), unique=True, nullable=False, index=True)
        user_email = Column(String(120), nullable=True, index=True)
        analysis_type = Column(String(20), nullable=False)  # 'image', 'video', 'audio'
        file_name = Column(String(255), nullable=False)
        file_size = Column(Integer)
        trust_score = Column(Float)
        is_fake = Column(Boolean)
        confidence = Column(Float)
        recommendation = Column(Text)
        analysis_time = Column(Float)
        timestamp = Column(DateTime, default=datetime.utcnow, index=True)
        
        def to_dict(self):
            return {
                'id': self.id,
                'analysis_id': self.analysis_id,
                'user_email': self.user_email or '',
                'analysis_type': self.analysis_type,
                'file_name': self.file_name,
                'file_size': self.file_size,
                'trust_score': self.trust_score,
                'is_fake': self.is_fake,
                'confidence': self.confidence,
                'recommendation': self.recommendation or '',
                'analysis_time': self.analysis_time,
                'timestamp': self.timestamp.isoformat() if self.timestamp else None
            }
    
    # Assign to module-level globals
    User = UserModel
    SignupHistory = SignupHistoryModel
    LoginHistory = LoginHistoryModel
    AnalysisResult = AnalysisResultModel
    
    # Return model classes for use in the app
    return {
        'User': User,
        'SignupHistory': SignupHistory,
        'LoginHistory': LoginHistory,
        'AnalysisResult': AnalysisResult
    }


# ============================================
# Firestore Collection Schemas (for reference)
# ============================================

"""
Firestore Collections Structure:

1. users (Collection):
   Document ID: user_email (e.g., "user@example.com")
   Fields:
   {
       email: string,
       full_name: string,
       phone_number: string,
       date_of_birth: string,
       country: string,
       occupation: string,
       created_at: timestamp,
       last_login: timestamp,
       total_analyses: number,
       updated_at: timestamp
   }
   
   Sub-collection: analysis_logs
   Document ID: anl_YYYY-MM-DD_HH-MM-SS-uid
   Fields:
   {
       analysis_id: string,
       analysis_type: string,
       file_name: string,
       is_fake: boolean,
       confidence: float,
       trust_score: float,
       timestamp: timestamp
   }

2. signup_history (Collection):
   Document ID: signup_YYYY-MM-DD_HH-MM-SS-uid
   Fields:
   {
       email: string,
       full_name: string,
       phone_number: string,
       date_of_birth: string,
       country: string,
       occupation: string,
       timestamp: timestamp,
       event_type: string (="signup"),
       status: string (="success")
   }

3. login_history (Collection):
   Document ID: login_YYYY-MM-DD_HH-MM-SS-uid
   Fields:
   {
       email: string,
       timestamp: timestamp,
       event_type: string (="login"),
       status: string (="success"),
       ip_address: string,
       user_agent: string
   }

4. analysis_results (Collection):
   Document ID: analysis_YYYY-MM-DD_HH-MM-SS-uid
   Fields:
   {
       user_email: string,
       analysis_type: string,
       file_name: string,
       file_size: number,
       trust_score: decimal,
       is_fake: boolean,
       confidence: decimal,
       recommendation: string,
       analysis_time: decimal,
       timestamp: timestamp
   }
"""
