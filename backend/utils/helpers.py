import os
import json
import logging

logger = logging.getLogger(__name__)

def generate_response(status, data=None, error=None):
    """
    Generate standardized API response
    
    Args:
        status: Response status ('success' or 'error')
        data: Response data dictionary
        error: Error message
        
    Returns:
        Dictionary formatted for JSON response
    """
    response = {
        'status': status,
        'timestamp': str(os.popen('date /t').read().strip())
    }
    
    if data:
        response.update(data)
    
    if error:
        response['error'] = error
    
    return response

def get_file_info(filepath):
    """
    Get file information
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file info
    """
    try:
        stat_info = os.stat(filepath)
        
        return {
            'path': filepath,
            'size': stat_info.st_size,
            'size_mb': round(stat_info.st_size / (1024 * 1024), 2),
            'exists': os.path.exists(filepath)
        }
    except Exception as e:
        logger.error(f"Error getting file info: {str(e)}")
        return {
            'path': filepath,
            'size': 0,
            'size_mb': 0,
            'exists': False
        }

def format_analysis_time(seconds):
    """
    Format analysis time in human-readable format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string
    """
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = seconds / 60
        return f"{minutes:.2f}m"

def format_file_size(bytes_size):
    """
    Format file size in human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    
    return f"{bytes_size:.2f} TB"

def log_analysis(analysis_type, file_name, trust_score, is_fake):
    """
    Log analysis result
    
    Args:
        analysis_type: Type of analysis ('image', 'video', 'audio')
        file_name: Name of analyzed file
        trust_score: Trust score (0-100)
        is_fake: Whether detected as fake
    """
    try:
        log_entry = {
            'type': analysis_type,
            'file': file_name,
            'score': trust_score,
            'is_fake': is_fake,
            'timestamp': str(os.popen('date /t').read().strip())
        }
        
        logger.info(f"Analysis: {json.dumps(log_entry)}")
        
    except Exception as e:
        logger.error(f"Error logging analysis: {str(e)}")

def clean_uploads(max_age_hours=24):
    """
    Clean up old uploaded files
    
    Args:
        max_age_hours: Maximum age of files to keep
    """
    try:
        import time
        uploads_dir = 'uploads'
        
        if not os.path.exists(uploads_dir):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(uploads_dir):
            filepath = os.path.join(uploads_dir, filename)
            
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    logger.info(f"Removed old file: {filename}")
    
    except Exception as e:
        logger.error(f"Error cleaning uploads: {str(e)}")
