"""
Deepfake Detection API Routes
Provides endpoints for analyzing images and videos for deepfakes
"""

import os
import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
from functools import wraps
import jwt

deepfake_bp = Blueprint('deepfake', __name__, url_prefix='/api/deepfake')
logger = logging.getLogger(__name__)

# Import from app context
def get_deepfake_service():
    """Lazy import to use multi-model ensemble service"""
    from models.multi_model_deepfake_service import get_multi_model_deepfake_service
    return get_multi_model_deepfake_service()

def get_deepfake_model():
    """Import deepfake result model"""
    from models.deepfake_result import DeepfakeDetectionResult
    return DeepfakeDetectionResult

def get_db():
    """Get database instance from Flask app"""
    from flask import current_app
    return current_app.extensions.get('sqlalchemy').db

def get_jwt_secret():
    """Get JWT secret from Flask app"""
    from flask import current_app
    return current_app.config.get('JWT_SECRET', 'your-secret-key')

def get_allowed_extensions():
    """Get allowed file extensions"""
    return {
        'image': {'png', 'jpg', 'jpeg', 'bmp', 'gif'},
        'video': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv'},
        'audio': {'wav', 'mp3', 'm4a', 'aac', 'ogg', 'flac'},
    }

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in get_allowed_extensions().get(file_type, set())

def token_required(f):
    """Decorator to protect endpoints requiring authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            # Allow anonymous requests but track them
            request.user_email = 'anonymous'
            return f(*args, **kwargs)
        
        try:
            data = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
            request.user_email = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

# ============================================
# DEEPFAKE DETECTION ENDPOINTS
# ============================================

@deepfake_bp.route('/health', methods=['GET'])
def deepfake_health():
    """Check deepfake detection service health"""
    try:
        service = get_deepfake_service()
        return jsonify({
            'status': 'healthy',
            'service': 'Deepfake Detection',
            'model_version': service.model_version,
            'device': str(service.device),
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@deepfake_bp.route('/analyze/image', methods=['POST'])
@token_required
def analyze_image():
    """
    Analyze a single image for deepfake artifacts
    
    Expected: 
    - file: image file (multipart form-data)
    
    Returns:
    - is_fake: boolean
    - fake_confidence: float (0-1)
    - real_confidence: float (0-1)
    - prediction: dict with confidence scores
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'File type not allowed. Allowed: png, jpg, jpeg, bmp, gif'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Process image
            service = get_deepfake_service()
            result = service.process_file(file_path, 'image')
            
            # Save to database
            try:
                db = get_db()
                DeepfakeResult = get_deepfake_model()
                
                detection_result = DeepfakeResult(
                    user_email=getattr(request, 'user_email', 'anonymous'),
                    file_name=filename,
                    file_path=file_path,
                    file_type='image',
                    file_size=file_size,
                    is_fake=result['is_fake'],
                    fake_confidence=result['fake_confidence'],
                    real_confidence=result['real_confidence'],
                    prediction_result=result['prediction'],
                    processing_time=result['processing_time'],
                    model_version=result['model_version']
                )
                
                db.session.add(detection_result)
                db.session.commit()
                logger.info(f"✅ Detection result saved to database: {detection_result.id}")
            except Exception as db_error:
                logger.warning(f"Could not save to database: {str(db_error)}")
            
            return jsonify({
                'success': True,
                'file_name': filename,
                'file_size': file_size,
                'is_fake': result['is_fake'],
                'fake_confidence': result['fake_confidence'],
                'real_confidence': result['real_confidence'],
                'models_used': result.get('models_used', 1),
                'model_predictions': result['prediction'].get('model_predictions', {}),
                'processing_time': round(result['processing_time'], 2),
                'model_version': result['model_version'],
                'recommendation': 'LIKELY MANIPULATED/AI-GENERATED - High Risk' if result['is_fake'] else 'Appears AUTHENTIC - Low Risk'
            }), 200
        
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file_path}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deepfake_bp.route('/analyze/video', methods=['POST'])
@token_required
def analyze_video():
    """
    Analyze a video for deepfake artifacts
    
    Expected:
    - file: video file (multipart form-data)
    - num_frames: optional, number of frames to analyze (default: 5)
    
    Returns:
    - is_fake: boolean
    - fake_confidence: float (0-1)
    - real_confidence: float (0-1)
    - prediction: dict with average confidence scores
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'File type not allowed. Allowed: mp4, avi, mov, mkv, flv, wmv'}), 400
        
        # Get optional parameters
        num_frames = request.form.get('num_frames', 5, type=int)
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Process video
            service = get_deepfake_service()
            result = service.process_file(file_path, 'video')
            
            # Save to database
            try:
                db = get_db()
                DeepfakeResult = get_deepfake_model()
                
                detection_result = DeepfakeResult(
                    user_email=getattr(request, 'user_email', 'anonymous'),
                    file_name=filename,
                    file_path=file_path,
                    file_type='video',
                    file_size=file_size,
                    is_fake=result['is_fake'],
                    fake_confidence=result['fake_confidence'],
                    real_confidence=result['real_confidence'],
                    prediction_result=result['prediction'],
                    processing_time=result['processing_time'],
                    model_version=result['model_version'],
                    notes=f"Analyzed {num_frames} frames"
                )
                
                db.session.add(detection_result)
                db.session.commit()
                logger.info(f"✅ Detection result saved to database: {detection_result.id}")
            except Exception as db_error:
                logger.warning(f"Could not save to database: {str(db_error)}")
            
            return jsonify({
                'success': True,
                'file_name': filename,
                'file_size': file_size,
                'frames_analyzed': num_frames,
                'is_fake': result['is_fake'],
                'fake_confidence': result['fake_confidence'],
                'real_confidence': result['real_confidence'],
                'models_used': result.get('models_used', 1),
                'processing_time': round(result['processing_time'], 2),
                'model_version': result['model_version'],
                'recommendation': 'Likely FAKE - Handle with caution' if result['is_fake'] else 'Likely AUTHENTIC - Appears genuine'
            }), 200
        
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file_path}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deepfake_bp.route('/analyze/audio', methods=['POST'])
@token_required
def analyze_audio():
    """
    Analyze audio for deepfake artifacts (voice cloning, synthesis, etc.)
    
    Expected:
    - file: audio file (multipart form-data)
    
    Returns:
    - is_fake: boolean
    - fake_confidence: float (0-1)
    - real_confidence: float (0-1)
    - prediction: dict with confidence scores
    
    Supported formats: WAV, MP3, M4A, AAC, OGG, FLAC
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, 'audio'):
            return jsonify({'error': 'File type not allowed. Allowed: wav, mp3, m4a, aac, ogg, flac'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Process audio
            service = get_deepfake_service()
            result = service.process_file(file_path, 'audio')
            
            # Save to database
            try:
                db = get_db()
                DeepfakeResult = get_deepfake_model()
                
                detection_result = DeepfakeResult(
                    user_email=getattr(request, 'user_email', 'anonymous'),
                    file_name=filename,
                    file_path=file_path,
                    file_type='audio',
                    file_size=file_size,
                    is_fake=result['is_fake'],
                    fake_confidence=result['fake_confidence'],
                    real_confidence=result['real_confidence'],
                    prediction_result=result['prediction'],
                    processing_time=result['processing_time'],
                    model_version=result['model_version'],
                    notes="Audio deepfake detection using Wav2Vec2 + BiGRU+Attention"
                )
                
                db.session.add(detection_result)
                db.session.commit()
                logger.info(f"✅ Audio detection result saved to database: {detection_result.id}")
            except Exception as db_error:
                logger.warning(f"Could not save to database: {str(db_error)}")
            
            return jsonify({
                'success': True,
                'file_name': filename,
                'file_size': file_size,
                'is_fake': result['is_fake'],
                'fake_confidence': result['fake_confidence'],
                'real_confidence': result['real_confidence'],
                'models_used': result.get('models_used', 1),
                'processing_time': round(result['processing_time'], 2),
                'model_version': result['model_version'],
                'recommendation': 'Likely SYNTHETIC VOICE - Possible deepfake' if result['is_fake'] else 'Likely AUTHENTIC VOICE - Appears genuine',
                'details': 'Detects voice cloning, speech synthesis, and audio manipulation'
            }), 200
        
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Could not delete temp file {file_path}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deepfake_bp.route('/history', methods=['GET'])
@token_required
def get_user_detection_history():
    """Get detection history for authenticated user"""
    try:
        user_email = getattr(request, 'user_email', None)
        
        if not user_email or user_email == 'anonymous':
            return jsonify({'error': 'Authentication required'}), 401
        
        db = get_db()
        DeepfakeResult = get_deepfake_model()
        
        # Get limit and offset from query parameters
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query results
        results = DeepfakeResult.query\
            .filter_by(user_email=user_email)\
            .order_by(DeepfakeResult.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        total_count = DeepfakeResult.query.filter_by(user_email=user_email).count()
        
        return jsonify({
            'success': True,
            'user_email': user_email,
            'total_count': total_count,
            'results': [r.to_dict() for r in results]
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@deepfake_bp.route('/stats', methods=['GET'])
@token_required
def get_detection_stats():
    """Get detection statistics for authenticated user"""
    try:
        user_email = getattr(request, 'user_email', None)
        
        if not user_email or user_email == 'anonymous':
            return jsonify({'error': 'Authentication required'}), 401
        
        db = get_db()
        DeepfakeResult = get_deepfake_model()
        
        results = DeepfakeResult.query.filter_by(user_email=user_email).all()
        
        if not results:
            return jsonify({
                'success': True,
                'user_email': user_email,
                'total_analyses': 0,
                'fake_detected': 0,
                'authentic_detected': 0,
                'accuracy_metrics': {}
            }), 200
        
        total = len(results)
        fake_count = sum(1 for r in results if r.is_fake)
        real_count = total - fake_count
        
        # Average confidence scores
        avg_fake_conf = sum(r.fake_confidence for r in results) / total if results else 0
        avg_real_conf = sum(r.real_confidence for r in results) / total if results else 0
        
        return jsonify({
            'success': True,
            'user_email': user_email,
            'total_analyses': total,
            'fake_detected': fake_count,
            'authentic_detected': real_count,
            'accuracy_metrics': {
                'avg_fake_confidence': round(avg_fake_conf, 3),
                'avg_real_confidence': round(avg_real_conf, 3),
                'fake_percentage': round((fake_count / total) * 100, 2) if total > 0 else 0
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
