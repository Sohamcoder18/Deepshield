# 🚀 Deployment & Getting Started Guide

## Quick Start (5 Minutes)

### 1. **Start the Flask Backend**
```bash
cd backend
python app.py
```

✅ You'll see:
```
✅ Deepfake detection service initialized successfully!
✅ Deepfake detection routes registered!
Starting DeepShield Backend Server...
Running on http://0.0.0.0:5000
```

### 2. **Test the Service**

**Via PowerShell (Windows):**
```powershell
.\test_api.ps1
```

**Via Bash (Mac/Linux):**
```bash
./test_api.sh
```

**Manual Test (Any OS):**
```bash
# Check health
curl http://localhost:5000/api/deepfake/health

# Analyze an image
curl -X POST http://localhost:5000/api/deepfake/analyze/image \
  -F "file=@test_image.jpg"
```

### 3. **Or Use Gradio UI**
```bash
python deepfake_classifier.py
# Opens: http://localhost:7860
```

---

## Installation

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Existing environment should have:
# - Flask
# - SQLAlchemy  
# - JWT
# - Transformers
# - Torch
# - Pillow
# - Gradio
```

### Install Missing Packages (if needed)
```bash
pip install transformers torch pillow gradio hf_hub flask-cors
```

### Models Auto-Download
- SIGLIP model downloads automatically on first run
- Size: ~350MB (will be cached)
- This only happens once

---

## Configuration

### Flask App Settings
```python
# In app.py - Auto-configured:
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['JWT_SECRET'] = 'from .env'
```

### Environment Variables (.env)
```
JWT_SECRET=your-secret-key-here
MONGODB_URI=mongodb+srv://...  # Optional
GROQ_API_KEY=your-groq-key     # Optional
BREVO_API_KEY=your-brevo-key   # Optional
```

### Database Configuration
```python
# SQLite (Primary)
sqlite:///deepfake_detection.db

# MongoDB (Optional)
# Falls back to SQLite if not available
```

---

## File Upload Limits

| Setting | Value |
|---------|-------|
| Max file size | 500 MB |
| Image formats | png, jpg, jpeg, bmp, gif |
| Video formats | mp4, avi, mov, mkv, flv, wmv |
| Processing timeout | 300 seconds |

---

## API Documentation

### Health Check
```bash
GET /api/deepfake/health

Response:
{
  "status": "healthy",
  "service": "Deepfake Detection",
  "model_version": "siglip-v1-pretrained",
  "device": "cuda" or "cpu",
  "timestamp": "2026-02-15T10:30:00"
}
```

### Analyze Image
```bash
POST /api/deepfake/analyze/image
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)

Response:
{
  "success": true,
  "file_name": "image.jpg",
  "file_size": 102400,
  "is_fake": false,
  "fake_confidence": 0.234,
  "real_confidence": 0.766,
  "prediction": {"fake": 0.234, "real": 0.766},
  "processing_time": 0.45,
  "recommendation": "Likely AUTHENTIC - Appears genuine"
}
```

### Analyze Video
```bash
POST /api/deepfake/analyze/video
Content-Type: multipart/form-data

Parameters:
- file: Video file (required)
- num_frames: Number of frames to analyze (optional, default: 5)

Response:
{
  "success": true,
  "file_name": "video.mp4",
  "file_size": 5242880,
  "frames_analyzed": 5,
  "is_fake": true,
  "fake_confidence": 0.892,
  "real_confidence": 0.108,
  "processing_time": 2.34,
  "recommendation": "Likely FAKE - Handle with caution"
}
```

### Get Detection History
```bash
GET /api/deepfake/history?limit=20&offset=0
Authorization: Bearer YOUR_JWT_TOKEN

Response:
{
  "success": true,
  "user_email": "user@example.com",
  "total_count": 25,
  "results": [
    {
      "id": 1,
      "file_name": "video.mp4",
      "is_fake": true,
      "fake_confidence": 0.892,
      ...
    }
  ]
}
```

### Get User Statistics
```bash
GET /api/deepfake/stats
Authorization: Bearer YOUR_JWT_TOKEN

Response:
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

---

## Usage Examples

### Python Script
```python
# Direct service usage
from models.deepfake_service import DeepfakeDetectionService

service = DeepfakeDetectionService()

# Analyze image
result = service.classify_image("image.jpg")
print(f"Fake: {result['fake']}, Real: {result['real']}")

# Analyze video
result = service.classify_video("video.mp4", num_frames=10)
print(f"Is Fake: {result['fake'] > result['real']}")
```

### With Database
```python
from app import app, db
from utils.deepfake_db_utils import save_detection_result

with app.app_context():
    result = service.process_file("video.mp4", 'video')
    
    saved = save_detection_result(
        db, "user@example.com", "video.mp4", 
        "/path/video.mp4", "video", 5242880,
        result['is_fake'], result['fake_confidence'],
        result['real_confidence'], result['prediction'],
        result['processing_time'], result['model_version']
    )
    
    print(f"Saved with ID: {saved.id}")
```

### Batch Processing
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

---

## Troubleshooting

### Issue: Model fails to load
```
ERROR: Can't download model from HF Hub
```
**Solution:**
- Check internet connection
- Try: `pip install --upgrade transformers`
- Set HF_TOKEN if using private models

### Issue: CUDA out of memory
```
ERROR: CUDA out of memory
```
**Solution:**
- GPU not available, falls back to CPU automatically
- Reduce `num_frames` parameter

### Issue: Database errors
```
ERROR: Can't access SQLite database
```
**Solution:**
- Check folder permissions
- Delete corrupted `.db` file
- App recreates schema on startup

### Issue: API returns 413 error
```
413 File Too Large
```
**Solution:**
- File exceeds 500MB limit
- Split into smaller files

### Issue: Slow video processing
- Processing time depends on:
  - Video resolution
  - Video codec
  - num_frames parameter
  - GPU availability
- Expected: 2-5 seconds for typical video

---

## Performance Tuning

### For Faster Processing
```python
# Reduce frame count
result = service.classify_video("video.mp4", num_frames=3)  # ~2 sec

# Use GPU
import torch
torch.cuda.is_available()  # True = GPU available
```

### For Better Accuracy
```python
# Increase frame count
result = service.classify_video("video.mp4", num_frames=10)  # ~4 sec
```

### For Batch Processing
```python
# Process multiple files
results = bulk_process_and_save(db, service, file_list, user_email)
```

---

## Monitoring

### Check Logs
```bash
# Watch Flask logs
python app.py  # Logs appear in console
```

### Database Statistics
```python
from utils.deepfake_db_utils import get_user_stats

stats = get_user_stats(db, "user@example.com")
print(stats)
```

### API Health
```bash
curl http://localhost:5000/api/deepfake/health | jq
```

---

## Deployment to Production

### Docker Setup
```dockerfile
FROM python:3.10

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### NGINX Proxy
```nginx
server {
    listen 80;
    server_name api.deepshield.com;

    location /api/deepfake/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Authorization $http_authorization;
    }
}
```

### Systemd Service
```ini
[Unit]
Description=DeepShield Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/app/backend
ExecStart=/usr/bin/python3 app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## Testing

### Run Test Suite
```bash
python test_deepfake_classifier.py
```

### Run Demo
```bash
python demo_deepfake.py
```

### Manual API Tests
```bash
# PowerShell
.\test_api.ps1

# Bash
./test_api.sh
```

---

## Support & Help

### Documentation
- `DEEPFAKE_INTEGRATION_README.md` - Complete API reference
- `FINAL_SUMMARY.md` - Project overview
- `demo_deepfake.py` - Code examples

### Testing Tools
- `test_api.ps1` - PowerShell testing
- `test_api.sh` - Bash testing
- `test_deepfake_classifier.py` - Dataset testing

### Common Commands
```bash
# Start app
python app.py

# Test health
curl http://localhost:5000/api/deepfake/health

# Analyze image
curl -X POST http://localhost:5000/api/deepfake/analyze/image \
  -F "file=@test.jpg"

# View database
sqlite3 instance/deepfake_detection.db ".tables"

# Export results
sqlite3 instance/deepfake_detection.db "SELECT * FROM deepfake_detection_results;" > results.csv
```

---

## Next Steps

1. **Start the server:** `python app.py`
2. **Test the API:** Use `test_api.ps1` or `test_api.sh`
3. **Integrate with frontend:** Connect to `/api/deepfake/*` endpoints
4. **Monitor results:** Check database and logs
5. **Scale up:** Use batch processing for multiple files

**You're ready to go!** 🎉
