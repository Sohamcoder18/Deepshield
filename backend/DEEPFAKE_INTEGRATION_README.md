# Deepfake Detection Integration

Complete integration of the pretrained SIGLIP deepfake detection model with Flask backend, database storage, and API endpoints.

## 📋 Components

### 1. **Deepfake Detection Service** (`models/deepfake_service.py`)
- Loads pretrained model: `prithivMLmods/deepfake-detector-model-v1`
- Supports image and video analysis
- Extracts video frames and averages predictions
- GPU-enabled (falls back to CPU)
- Thread-safe singleton pattern

**Key Methods:**
- `classify_image()` - Analyze single image
- `classify_video()` - Analyze video (multiple frames)
- `process_file()` - Universal file processor

### 2. **Database Model** (`models/deepfake_result.py`)
Stores detection results with:
- User email and file metadata
- Detection results (is_fake, confidence scores)
- Processing metrics (time, model version)
- Full prediction dictionary
- Timestamps and notes

### 3. **API Routes** (`routes/deepfake_routes.py`)
RESTful endpoints for analysis and history:

#### Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---|
| GET | `/api/deepfake/health` | Service health check | No |
| POST | `/api/deepfake/analyze/image` | Analyze image file | Optional |
| POST | `/api/deepfake/analyze/video` | Analyze video file | Optional |
| GET | `/api/deepfake/history` | Get user's analysis history | Yes |
| GET | `/api/deepfake/stats` | Get user's statistics | Yes |

### 4. **Database Utilities** (`utils/deepfake_db_utils.py`)
Helper functions for database operations:
- `save_detection_result()` - Save single result
- `get_user_results()` - Retrieve user's results
- `get_user_stats()` - Calculate statistics
- `export_results_to_csv()` - Export data
- `bulk_process_and_save()` - Process multiple files

## 🚀 Quick Start

### 1. Initialize Flask App
The deepfake service is automatically loaded when the Flask app starts:

```python
from app import app
# Service initializes automatically
# Routes are registered automatically
```

### 2. Test the API

**Analyze an image:**
```bash
curl -X POST http://localhost:5000/api/deepfake/analyze/image \
  -F "file=@test_image.jpg"
```

**Analyze a video:**
```bash
curl -X POST http://localhost:5000/api/deepfake/analyze/video \
  -F "file=@test_video.mp4" \
  -F "num_frames=5"
```

**Check service health:**
```bash
curl http://localhost:5000/api/deepfake/health
```

### 3. Authenticated Requests

For features requiring authentication:

```bash
# Get detection history
curl -X GET http://localhost:5000/api/deepfake/history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get user statistics
curl -X GET http://localhost:5000/api/deepfake/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 API Response Examples

### Image Analysis Response
```json
{
  "success": true,
  "file_name": "test.jpg",
  "file_size": 102400,
  "is_fake": false,
  "fake_confidence": 0.234,
  "real_confidence": 0.766,
  "prediction": {
    "fake": 0.234,
    "real": 0.766
  },
  "processing_time": 0.45,
  "model_version": "siglip-v1-pretrained",
  "recommendation": "Likely AUTHENTIC - Appears genuine"
}
```

### Video Analysis Response
```json
{
  "success": true,
  "file_name": "test.mp4",
  "file_size": 5242880,
  "frames_analyzed": 5,
  "is_fake": true,
  "fake_confidence": 0.892,
  "real_confidence": 0.108,
  "prediction": {
    "fake": 0.892,
    "real": 0.108
  },
  "processing_time": 2.34,
  "model_version": "siglip-v1-pretrained",
  "recommendation": "Likely FAKE - Handle with caution"
}
```

### Detection History Response
```json
{
  "success": true,
  "user_email": "user@example.com",
  "total_count": 25,
  "results": [
    {
      "id": 1,
      "file_name": "test.mp4",
      "file_type": "video",
      "file_size": 5242880,
      "is_fake": true,
      "fake_confidence": 0.892,
      "real_confidence": 0.108,
      "prediction_result": {...},
      "processing_time": 2.34,
      "model_version": "siglip-v1-pretrained",
      "created_at": "2026-02-15T10:30:00"
    }
  ]
}
```

### User Statistics Response
```json
{
  "success": true,
  "user_email": "user@example.com",
  "total_analyses": 25,
  "fake_detected": 18,
  "authentic_detected": 7,
  "accuracy_metrics": {
    "avg_fake_confidence": 0.812,
    "avg_real_confidence": 0.188,
    "fake_percentage": 72.0
  }
}
```

## 🔧 Programmatic Usage

### Direct Service Usage
```python
from models.deepfake_service import DeepfakeDetectionService

service = DeepfakeDetectionService()

# Analyze image
result = service.classify_image("path/to/image.jpg")
print(f"Fake: {result['fake']}, Real: {result['real']}")

# Analyze video
result = service.classify_video("path/to/video.mp4", num_frames=5)
print(f"Is Fake: {result['fake'] > result['real']}")

# Process any file
result = service.process_file("path/to/file", 'video')
```

### With Database Integration
```python
from app import app, db
from models.deepfake_service import get_deepfake_service
from utils.deepfake_db_utils import save_detection_result, get_user_stats

with app.app_context():
    service = get_deepfake_service()
    
    # Process file
    result = service.process_file("video.mp4", 'video')
    
    # Save to database
    db_result = save_detection_result(
        db=db,
        user_email="user@example.com",
        file_name="video.mp4",
        file_path="/path/to/video.mp4",
        file_type='video',
        file_size=5242880,
        is_fake=result['is_fake'],
        fake_confidence=result['fake_confidence'],
        real_confidence=result['real_confidence'],
        prediction_result=result['prediction'],
        processing_time=result['processing_time'],
        model_version=result['model_version']
    )
    
    # Get user statistics
    stats = get_user_stats(db, "user@example.com")
    print(f"User has {stats['total_analyses']} analyses")
```

### Bulk Processing
```python
from utils.deepfake_db_utils import bulk_process_and_save

files = [
    ("video1.mp4", "video"),
    ("image1.jpg", "image"),
    ("video2.mp4", "video")
]

results = bulk_process_and_save(db, service, files, "user@example.com")
print(f"Processed {len(results)} files")
```

## 📈 Test Results

From `test_deepfake_classifier.py`:
- **Overall Accuracy: 76%** (19/25 correct)
- **FaceShifter: 100%** (5/5 correct)
- **FaceSwap: 100%** (5/5 correct)
- **Face2Face: 80%** (4/5 correct)
- **NeuralTextures: 80%** (4/5 correct)
- **Original (Real): 20%** (1/5 correct) - Model tends to flag real videos

## ⚙️ Configuration

### Environment Variables
```
# Model selection
DEEPFAKE_MODEL=prithivMLmods/deepfake-detector-model-v1

# API configuration
JWT_SECRET=your-secret-key
MAX_CONTENT_LENGTH=500M
```

### Supported File Types

**Images:**
- png, jpg, jpeg, bmp, gif

**Videos:**
- mp4, avi, mov, mkv, flv, wmv

**Max File Size:** 500MB

## 📝 Testing

### Run Demo Script
```bash
cd backend
python demo_deepfake.py
```

This demonstrates:
1. Direct service usage
2. Database integration
3. Bulk processing
4. Available API endpoints

### Run Test Suite
```bash
python test_deepfake_classifier.py
```

Tests on dataset videos and shows predictions with accuracy metrics.

## 🐛 Troubleshooting

### Model Loading Issues
```python
# Check if model loads
from models.deepfake_service import DeepfakeDetectionService
service = DeepfakeDetectionService()
# Will log if successful or error
```

### Database Errors
- Ensure SQLite is properly initialized
- Check that `DeepfakeDetectionResult` model is imported
- MongoDB fallback is available if configured

### Video Processing Errors
- Ensure OpenCV (cv2) is installed
- Check video codec support
- Verify file is valid MP4/AVI format

### GPU Issues
```python
# Force CPU
import torch
torch.device('cpu')
```

## 📚 File Structure
```
backend/
├── models/
│   ├── deepfake_service.py       # Core detection service
│   ├── deepfake_result.py        # Database model
│   └── ...
├── routes/
│   ├── deepfake_routes.py        # API endpoints
│   └── ...
├── utils/
│   ├── deepfake_db_utils.py      # Database utilities
│   └── ...
├── app.py                         # Main Flask app (updated)
├── deepfake_classifier.py         # Gradio interface
├── test_deepfake_classifier.py    # Test script
└── demo_deepfake.py              # Demo script
```

## 🤝 Integration Notes

- ✅ Automatically initializes with Flask app
- ✅ Registers routes automatically
- ✅ Thread-safe service instance
- ✅ Graceful error handling
- ✅ Optional authentication
- ✅ SQLite + MongoDB support
- ✅ Rate limiting built-in
- ✅ CSV export capability

## 📞 Support

For issues or features:
1. Check logs: `logger.info()` statements throughout
2. Run demo script: `python demo_deepfake.py`
3. Test API: Use curl/Postman with examples above
4. Verify model: `python -c "from models.deepfake_service import DeepfakeDetectionService; DeepfakeDetectionService()"`
