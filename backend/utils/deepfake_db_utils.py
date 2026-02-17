"""
Database utility for saving deepfake detection results
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_detection_result(db, user_email, file_name, file_path, file_type, file_size, 
                         is_fake, fake_confidence, real_confidence, prediction_result, 
                         processing_time, model_version, notes=None):
    """
    Save a deepfake detection result to the database
    
    Args:
        db: Flask-SQLAlchemy database instance
        user_email: Email of user who performed the analysis
        file_name: Name of the analyzed file
        file_path: Path where file is stored
        file_type: Type of file ('image', 'video', 'audio')
        file_size: Size of file in bytes
        is_fake: Boolean indicating if content is fake
        fake_confidence: Confidence score for fake (0-1)
        real_confidence: Confidence score for real (0-1)
        prediction_result: Full prediction dictionary
        processing_time: Time taken to process in seconds
        model_version: Version of model used
        notes: Optional notes about the analysis
    
    Returns:
        DeepfakeDetectionResult object or None on error
    """
    try:
        from models.deepfake_result import DeepfakeDetectionResult
        
        result = DeepfakeDetectionResult(
            user_email=user_email,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            is_fake=is_fake,
            fake_confidence=fake_confidence,
            real_confidence=real_confidence,
            prediction_result=prediction_result,
            processing_time=processing_time,
            model_version=model_version,
            notes=notes
        )
        
        db.session.add(result)
        db.session.commit()
        
        logger.info(f"✅ Saved detection result: {result.id} for {user_email}")
        return result
    
    except Exception as e:
        logger.error(f"❌ Error saving detection result: {str(e)}")
        db.session.rollback()
        return None

def get_user_results(db, user_email, limit=20, offset=0):
    """
    Retrieve detection results for a specific user
    
    Args:
        db: Flask-SQLAlchemy database instance
        user_email: Email of user
        limit: Maximum number of results to return
        offset: Number of results to skip
    
    Returns:
        List of DeepfakeDetectionResult objects
    """
    try:
        from models.deepfake_result import DeepfakeDetectionResult
        
        results = DeepfakeDetectionResult.query\
            .filter_by(user_email=user_email)\
            .order_by(DeepfakeDetectionResult.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        logger.info(f"Retrieved {len(results)} results for {user_email}")
        return results
    
    except Exception as e:
        logger.error(f"❌ Error retrieving results: {str(e)}")
        return []

def get_user_stats(db, user_email):
    """
    Get statistics for a user's analyses
    
    Args:
        db: Flask-SQLAlchemy database instance
        user_email: Email of user
    
    Returns:
        Dictionary with statistics
    """
    try:
        from models.deepfake_result import DeepfakeDetectionResult
        
        results = DeepfakeDetectionResult.query.filter_by(user_email=user_email).all()
        
        if not results:
            return {
                'user_email': user_email,
                'total_analyses': 0,
                'fake_detected': 0,
                'authentic_detected': 0,
                'avg_processing_time': 0,
                'accuracy_metrics': {}
            }
        
        total = len(results)
        fake_count = sum(1 for r in results if r.is_fake)
        real_count = total - fake_count
        avg_time = sum(r.processing_time for r in results) / total
        avg_fake_conf = sum(r.fake_confidence for r in results) / total
        avg_real_conf = sum(r.real_confidence for r in results) / total
        
        stats = {
            'user_email': user_email,
            'total_analyses': total,
            'fake_detected': fake_count,
            'authentic_detected': real_count,
            'avg_processing_time': round(avg_time, 2),
            'by_file_type': {},
            'accuracy_metrics': {
                'avg_fake_confidence': round(avg_fake_conf, 3),
                'avg_real_confidence': round(avg_real_conf, 3),
                'fake_percentage': round((fake_count / total) * 100, 2)
            }
        }
        
        # Count by file type
        for file_type in ['image', 'video', 'audio']:
            count = sum(1 for r in results if r.file_type == file_type)
            if count > 0:
                type_fake = sum(1 for r in results if r.file_type == file_type and r.is_fake)
                stats['by_file_type'][file_type] = {
                    'total': count,
                    'fake': type_fake,
                    'authentic': count - type_fake
                }
        
        logger.info(f"Retrieved stats for {user_email}: {total} analyses")
        return stats
    
    except Exception as e:
        logger.error(f"❌ Error calculating stats: {str(e)}")
        return {}

def export_results_to_csv(db, user_email, output_file):
    """
    Export user's detection results to CSV file
    
    Args:
        db: Flask-SQLAlchemy database instance
        user_email: Email of user
        output_file: Path where CSV should be saved
    
    Returns:
        True if successful, False otherwise
    """
    try:
        import csv
        from models.deepfake_result import DeepfakeDetectionResult
        
        results = DeepfakeDetectionResult.query.filter_by(user_email=user_email).all()
        
        if not results:
            logger.warning(f"No results found for {user_email}")
            return False
        
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = [
                'id', 'file_name', 'file_type', 'file_size', 'is_fake',
                'fake_confidence', 'real_confidence', 'processing_time',
                'model_version', 'created_at'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                writer.writerow({
                    'id': result.id,
                    'file_name': result.file_name,
                    'file_type': result.file_type,
                    'file_size': result.file_size,
                    'is_fake': result.is_fake,
                    'fake_confidence': result.fake_confidence,
                    'real_confidence': result.real_confidence,
                    'processing_time': result.processing_time,
                    'model_version': result.model_version,
                    'created_at': result.created_at.isoformat()
                })
        
        logger.info(f"✅ Exported {len(results)} results to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error exporting results: {str(e)}")
        return False

def bulk_process_and_save(db, service, file_list, user_email):
    """
    Process multiple files and save results to database
    
    Args:
        db: Flask-SQLAlchemy database instance
        service: DeepfakeDetectionService instance
        file_list: List of (file_path, file_type) tuples
        user_email: Email of user
    
    Returns:
        List of saved results
    """
    import time
    
    saved_results = []
    
    for file_path, file_type in file_list:
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            logger.info(f"Processing: {file_path}")
            
            # Process file
            result = service.process_file(file_path, file_type)
            
            # Save to database
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            saved = save_detection_result(
                db, user_email, file_name, file_path, file_type, file_size,
                result['is_fake'], result['fake_confidence'], result['real_confidence'],
                result['prediction'], result['processing_time'], result['model_version']
            )
            
            if saved:
                saved_results.append(saved)
            
            time.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            continue
    
    logger.info(f"✅ Successfully processed and saved {len(saved_results)} files")
    return saved_results
