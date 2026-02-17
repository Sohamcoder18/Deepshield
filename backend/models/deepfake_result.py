from datetime import datetime
from app import db

class DeepfakeDetectionResult(db.Model):
    """Model for storing deepfake detection results"""
    __tablename__ = 'deepfake_detection_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=True, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # 'image', 'video', 'audio'
    file_size = db.Column(db.Integer, nullable=False)
    
    # Detection Results
    is_fake = db.Column(db.Boolean, nullable=False)
    fake_confidence = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    real_confidence = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    prediction_result = db.Column(db.JSON, nullable=False)  # Full prediction dict
    
    # Additional Metrics
    processing_time = db.Column(db.Float, nullable=False)  # seconds
    model_version = db.Column(db.String(50), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_email': self.user_email,
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'is_fake': self.is_fake,
            'fake_confidence': round(self.fake_confidence, 3),
            'real_confidence': round(self.real_confidence, 3),
            'prediction_result': self.prediction_result,
            'processing_time': round(self.processing_time, 2),
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat(),
            'notes': self.notes
        }
