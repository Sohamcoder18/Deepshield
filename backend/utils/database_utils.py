"""
Database Utility Functions for DeepFake Detection System
Handles both SQLite and MongoDB operations
"""

import uuid
from datetime import datetime


class DatabaseManager:
    """Manages database operations for both SQLite and MongoDB"""
    
    def __init__(self, sqlite_db=None, mongo_db=None):
        """
        Initialize DatabaseManager
        
        Args:
            sqlite_db: SQLAlchemy database instance
            mongo_db: MongoDB database instance
        """
        self.sqlite_db = sqlite_db
        self.mongo_db = mongo_db
    
    def save_analysis_result(self, analysis_data, use_sqlite=True, use_mongodb=True):
        """
        Save analysis result to both or selected databases
        
        Args:
            analysis_data: Dictionary containing analysis results
            use_sqlite: Whether to save to SQLite (default: True)
            use_mongodb: Whether to save to MongoDB (default: True)
            
        Returns:
            Dictionary with save status and IDs
        """
        result = {
            'success': False,
            'sqlite_id': None,
            'mongodb_id': None,
            'errors': []
        }
        
        # Generate analysis ID if not provided
        if 'analysis_id' not in analysis_data:
            analysis_data['analysis_id'] = str(uuid.uuid4())
        
        # Add timestamp
        analysis_data['timestamp'] = datetime.utcnow().isoformat()
        
        # Save to SQLite
        if use_sqlite and self.sqlite_db is not None:
            try:
                from models.database_models import AnalysisResult
                sqlite_result = AnalysisResult(
                    analysis_id=analysis_data.get('analysis_id'),
                    analysis_type=analysis_data.get('analysis_type'),
                    file_name=analysis_data.get('file_name'),
                    file_size=analysis_data.get('file_size'),
                    trust_score=analysis_data.get('trust_score'),
                    is_fake=analysis_data.get('is_fake'),
                    confidence=analysis_data.get('confidence'),
                    recommendation=analysis_data.get('recommendation'),
                    analysis_time=analysis_data.get('analysis_time')
                )
                self.sqlite_db.session.add(sqlite_result)
                self.sqlite_db.session.commit()
                result['sqlite_id'] = sqlite_result.id
                result['success'] = True
            except Exception as e:
                self.sqlite_db.session.rollback()
                result['errors'].append(f"SQLite error: {str(e)}")
        
        # Save to MongoDB
        if use_mongodb and self.mongo_db is not None:
            try:
                mongo_result = self.mongo_db.analysis_results.insert_one(analysis_data)
                result['mongodb_id'] = str(mongo_result.inserted_id)
                result['success'] = True
            except Exception as e:
                result['errors'].append(f"MongoDB error: {str(e)}")
        
        return result
    
    def get_analysis_result(self, analysis_id, source='both'):
        """
        Retrieve analysis result from database
        
        Args:
            analysis_id: ID of the analysis
            source: 'sqlite', 'mongodb', or 'both' (default: 'both')
            
        Returns:
            Analysis result dictionary
        """
        result = {
            'sqlite': None,
            'mongodb': None
        }
        
        # Get from SQLite
        if source in ['sqlite', 'both'] and self.sqlite_db is not None:
            try:
                from models.database_models import AnalysisResult
                sqlite_result = AnalysisResult.query.filter_by(analysis_id=analysis_id).first()
                if sqlite_result:
                    result['sqlite'] = sqlite_result.to_dict()
            except Exception as e:
                pass
        
        # Get from MongoDB
        if source in ['mongodb', 'both'] and self.mongo_db is not None:
            try:
                from bson.objectid import ObjectId
                try:
                    if ObjectId.is_valid(analysis_id):
                        mongo_result = self.mongo_db.analysis_results.find_one({'_id': ObjectId(analysis_id)})
                    else:
                        mongo_result = self.mongo_db.analysis_results.find_one({'analysis_id': analysis_id})
                    
                    if mongo_result:
                        mongo_result['_id'] = str(mongo_result['_id'])
                        result['mongodb'] = mongo_result
                except Exception:
                    pass
            except Exception as e:
                pass
        
        return result
    
    def get_all_results(self, limit=100, source='both'):
        """
        Get all analysis results
        
        Args:
            limit: Maximum number of results to return
            source: 'sqlite', 'mongodb', or 'both' (default: 'both')
            
        Returns:
            Dictionary with results from selected sources
        """
        results = {
            'sqlite': [],
            'mongodb': []
        }
        
        # Get from SQLite
        if source in ['sqlite', 'both'] and self.sqlite_db is not None:
            try:
                from models.database_models import AnalysisResult
                sqlite_results = AnalysisResult.query.limit(limit).all()
                results['sqlite'] = [r.to_dict() for r in sqlite_results]
            except Exception as e:
                pass
        
        # Get from MongoDB
        if source in ['mongodb', 'both'] and self.mongo_db is not None:
            try:
                mongo_results = list(self.mongo_db.analysis_results.find().limit(limit))
                for r in mongo_results:
                    r['_id'] = str(r['_id'])
                results['mongodb'] = mongo_results
            except Exception as e:
                pass
        
        return results
    
    def save_fusion_result(self, fusion_data):
        """
        Save fusion result to both databases
        
        Args:
            fusion_data: Dictionary containing fusion results
            
        Returns:
            Fusion result ID
        """
        if 'fusion_id' not in fusion_data:
            fusion_data['fusion_id'] = str(uuid.uuid4())
        
        fusion_data['created_at'] = datetime.utcnow().isoformat()
        
        if self.mongo_db is not None:
            try:
                result = self.mongo_db.fusion_results.insert_one(fusion_data)
                return str(result.inserted_id)
            except Exception as e:
                return None
        
        return None
    
    def save_audit_log(self, user_id, action, analysis_id=None, status='success', ip_address=None):
        """
        Save audit log to MongoDB
        
        Args:
            user_id: User ID performing the action
            action: Action being performed
            analysis_id: Related analysis ID
            status: Status of the action
            ip_address: Client IP address
            
        Returns:
            Log entry ID
        """
        if self.mongo_db is None:
            return None
        
        log_entry = {
            'user_id': user_id,
            'action': action,
            'analysis_id': analysis_id,
            'status': status,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            result = self.mongo_db.audit_logs.insert_one(log_entry)
            return str(result.inserted_id)
        except Exception as e:
            return None
