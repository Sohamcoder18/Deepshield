# DeepShield Backend Setup Guide

## Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env file with your configuration
```

### 5. Create Required Directories
```bash
mkdir uploads
mkdir logs
mkdir models
```

### 6. Download Pre-trained Models
- Download XceptionNet model trained on FaceForensics++
- Place in `models/` folder
- Download Audio CNN model
- Place in `models/` folder

## Running the Server

### Development Mode
```bash
python app.py
```

Server will start at `http://localhost:5000`

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Models Status
```
GET /api/models/status
```

### Image Analysis
```
POST /api/analyze/image
```
**Parameters:** multipart form-data with file

**Response:**
```json
{
  "status": "success",
  "analysis_type": "image",
  "file_name": "image.jpg",
  "file_size": 2048576,
  "analysis_time": 2.34,
  "trust_score": 85.5,
  "is_fake": false,
  "confidence": 0.855,
  "xception_score": 85.5,
  "artifact_detection": 70.2,
  "recommendation": "This image appears authentic..."
}
```

### Video Analysis
```
POST /api/analyze/video
```
**Parameters:**
- file: video file
- frame_count: number of frames to analyze (optional, default: 15)

**Response:**
```json
{
  "status": "success",
  "analysis_type": "video",
  "file_name": "video.mp4",
  "duration": 45.5,
  "frames_analyzed": 15,
  "trust_score": 72.3,
  "is_fake": false,
  "suspicious_frames": 2,
  "temporal_consistency": 0.87,
  "consistency_score": 87.0,
  "recommendation": "Video appears authentic with good temporal consistency."
}
```

### Audio Analysis
```
POST /api/analyze/audio
```
**Parameters:** multipart form-data with file

**Response:**
```json
{
  "status": "success",
  "analysis_type": "audio",
  "file_name": "audio.wav",
  "duration": 15.3,
  "sample_rate": 44100,
  "trust_score": 78.9,
  "is_fake": false,
  "synthesis_probability": 21.1,
  "authenticity_score": 78.9,
  "spectral_consistency": 0.91,
  "recommendation": "Audio appears to be authentic human speech..."
}
```

### Fusion Analysis
```
POST /api/fusion/combine
```
**Body:**
```json
{
  "image_score": 85.5,
  "video_score": 72.3,
  "audio_score": 78.9
}
```

**Response:**
```json
{
  "status": "success",
  "fused_trust_score": 78.9,
  "final_verdict": "AUTHENTIC",
  "confidence": 0.889,
  "weights": {
    "image": 0.35,
    "video": 0.35,
    "audio": 0.30
  }
}
```

## Project Structure

```
backend/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment configuration template
├── README.md                  # This file
├── models/
│   ├── image_detector.py      # Image deepfake detection
│   ├── video_detector.py      # Video deepfake detection
│   ├── audio_detector.py      # Audio deepfake detection
│   └── fusion_logic.py        # Result fusion logic
├── utils/
│   ├── validators.py          # File validation
│   └── helpers.py             # Helper functions
├── uploads/                   # Temporary file uploads
├── logs/                      # Application logs
└── models/                    # Pre-trained model files

```

## Environment Variables

- `FLASK_ENV`: Flask environment (development/production)
- `DEBUG`: Enable debug mode
- `HOST`: Server host
- `PORT`: Server port
- `MAX_FILE_SIZE`: Maximum upload size in MB
- `VIDEO_FRAME_COUNT`: Default frames to analyze in videos
- `FUSION_*_WEIGHT`: Weights for fusion logic

## Testing

### Test Image Analysis
```bash
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/api/analyze/image
```

### Test Video Analysis
```bash
curl -X POST -F "file=@test_video.mp4" -F "frame_count=10" http://localhost:5000/api/analyze/video
```

### Test Audio Analysis
```bash
curl -X POST -F "file=@test_audio.wav" http://localhost:5000/api/analyze/audio
```

## Notes

1. Models are simulated for demonstration. Replace with actual pre-trained models.
2. File uploads are temporarily stored in `uploads/` folder and cleaned up after analysis.
3. Configure CORS origins in `.env` for frontend communication.
4. Use Gunicorn for production deployment instead of Flask's development server.

## Support

For issues or questions, check the logs in `logs/deepshield.log`
