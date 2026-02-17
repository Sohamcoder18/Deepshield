# Quick Reference Guide

## 🚀 Getting Started (5 Minutes)

### Step 1: Configure Environment
Edit `backend/.env`:
```env
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:YOUR_PASSWORD_HERE@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

### Step 2: Install Packages
```bash
cd backend
python -m pip install -r requirements.txt
```

### Step 3: Run Server
```bash
python app.py
```

### Step 4: Verify Setup
```bash
curl http://localhost:5000/api/db/status
```

Expected response:
```json
{
  "status": "ok",
  "databases": {
    "sqlite": "connected",
    "mongodb": "connected"
  }
}
```

---

## 📚 API Endpoints Quick Reference

### 1. Check Database Status
```bash
GET /api/db/status
```
**Use**: Verify both databases are operational

### 2. Save Analysis Result
```bash
POST /api/results/save
Content-Type: application/json

{
  "analysis_type": "image",
  "file_name": "test.jpg",
  "file_size": 102400,
  "trust_score": 85.5,
  "is_fake": false,
  "confidence": 0.92,
  "recommendation": "authentic",
  "analysis_time": 2.34
}
```
**Returns**: `analysis_id` (use to retrieve later)

### 3. Retrieve Analysis Result
```bash
GET /api/results/{analysis_id}
GET /api/results/{analysis_id}?source=sqlite
GET /api/results/{analysis_id}?source=mongodb
GET /api/results/{analysis_id}?source=both
```
**Use**: Get specific analysis details

### 4. Get All Results
```bash
GET /api/results
GET /api/results?limit=50
GET /api/results?source=sqlite
GET /api/results?source=mongodb
```
**Use**: Retrieve analysis history

---

## 🔄 Complete Workflow Example

### Scenario: Analyze an image and save result

**Step 1: Upload & Analyze Image**
```bash
curl -X POST http://localhost:5000/api/analyze/image \
  -F "file=@sample_image.jpg"
```

Response:
```json
{
  "status": "success",
  "analysis_type": "image",
  "file_name": "sample_image.jpg",
  "trust_score": 78.5,
  "is_fake": true,
  "confidence": 0.85,
  ...
}
```

**Step 2: Save to Database (NEW)**
```bash
curl -X POST http://localhost:5000/api/results/save \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "image",
    "file_name": "sample_image.jpg",
    "file_size": 102400,
    "trust_score": 78.5,
    "is_fake": true,
    "confidence": 0.85,
    "recommendation": "suspicious",
    "analysis_time": 2.5
  }'
```

Response:
```json
{
  "status": "success",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "sqlite_id": 1,
  "mongodb_id": "65b8c1a2f7e4b2c3d4e5f6g7"
}
```

**Step 3: Retrieve Result**
```bash
curl http://localhost:5000/api/results/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "status": "success",
  "data": {
    "sqlite": {
      "id": 1,
      "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
      "trust_score": 78.5,
      ...
    },
    "mongodb": {
      "_id": "65b8c1a2f7e4b2c3d4e5f6g7",
      "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
      "trust_score": 78.5,
      ...
    }
  }
}
```

---

## 💾 Database Query Examples

### Python with Requests
```python
import requests

BASE_URL = "http://localhost:5000"

# Save result
result_data = {
    "analysis_type": "image",
    "file_name": "test.jpg",
    "trust_score": 75.5,
    "is_fake": True,
    "confidence": 0.85,
    "recommendation": "suspicious",
    "analysis_time": 1.5,
    "file_size": 50000
}

response = requests.post(f"{BASE_URL}/api/results/save", json=result_data)
data = response.json()
analysis_id = data['analysis_id']

# Retrieve result
response = requests.get(f"{BASE_URL}/api/results/{analysis_id}")
print(response.json())
```

### JavaScript with Fetch
```javascript
const BASE_URL = "http://localhost:5000";

// Save result
const resultData = {
  analysis_type: "image",
  file_name: "test.jpg",
  trust_score: 75.5,
  is_fake: true,
  confidence: 0.85,
  recommendation: "suspicious",
  analysis_time: 1.5,
  file_size: 50000
};

const response = await fetch(`${BASE_URL}/api/results/save`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(resultData)
});

const data = await response.json();
const analysisId = data.analysis_id;

// Retrieve result
const getResponse = await fetch(`${BASE_URL}/api/results/${analysisId}`);
console.log(await getResponse.json());
```

---

## 🔧 Configuration Quick Reference

### .env File Template
```env
# MongoDB Connection (REQUIRED)
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:PASSWORD@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase

# Flask Configuration (OPTIONAL)
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (OPTIONAL)
SQLALCHEMY_DATABASE_URI=sqlite:///deepfake_detection.db

# Server Configuration (OPTIONAL)
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

### requirements.txt - New Packages
```
pymongo==3.11.4
sqlalchemy==2.0.0
flask-sqlalchemy==3.0.3
```

---

## 🎯 File Structure Overview

```
backend/
├── app.py                      ← UPDATED with DB config
├── requirements.txt            ← UPDATED with DB packages
├── .env                        ← NEW config file
├── models/
│   └── database_models.py      ← NEW SQLAlchemy models
├── utils/
│   └── database_utils.py       ← NEW Database Manager
└── Documentation/
    ├── DATABASE_SETUP.md
    ├── DATABASE_SUMMARY.md
    ├── QUICKSTART_DB.md
    ├── INTEGRATION_EXAMPLES.md
    ├── ARCHITECTURE.md
    └── IMPLEMENTATION_CHECKLIST.md
```

---

## ⚠️ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| MongoDB connection fails | Replace `<db_password>` in .env with actual password |
| "ModuleNotFoundError: No module named 'pymongo'" | Run: `python -m pip install -r requirements.txt` |
| "SQLite database is locked" | Restart app; ensure no other process uses DB file |
| "ConnectionFailure" | Check IP is whitelisted in MongoDB Atlas |
| "No module named 'flask_sqlalchemy'" | Run: `pip install flask-sqlalchemy` |

---

## 📊 Database Structure Summary

### SQLite Tables
- **analysis_results**: id, analysis_id, analysis_type, file_name, file_size, trust_score, is_fake, confidence, recommendation, analysis_time, timestamp
- **users**: id, username, email, created_at, analyses_count

### MongoDB Collections
- **analysis_results**: Flexible schema, stores all analysis types
- **users**: User profiles and metadata
- **fusion_results**: Combined multi-modal analysis results
- **audit_logs**: Activity tracking and compliance logs

---

## 🚀 Next Integration Steps

1. **Add database saving to detection endpoints**
   ```python
   db_result = db_manager.save_analysis_result({
       'analysis_type': 'image',
       'file_name': filename,
       'trust_score': results['trust_score'],
       ...
   })
   response['analysis_id'] = db_result['analysis_id']
   ```

2. **Test with sample data**
   - Use curl/Postman to test API endpoints
   - Verify data appears in both databases

3. **Monitor logs**
   - Check for database connection issues
   - Verify successful saves

4. **Add user authentication**
   - Link analyses to user IDs
   - Create user dashboard

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| DATABASE_SETUP.md | Comprehensive setup guide |
| DATABASE_SUMMARY.md | Feature overview & API reference |
| QUICKSTART_DB.md | Quick start checklist |
| INTEGRATION_EXAMPLES.md | Code examples & patterns |
| ARCHITECTURE.md | System architecture diagrams |
| IMPLEMENTATION_CHECKLIST.md | Task tracking & status |
| QUICK_REFERENCE.md | This file |

---

## 💡 Pro Tips

✅ **Use both databases** for redundancy
✅ **Save analysis results** immediately after detection
✅ **Include analysis_id** in API responses
✅ **Monitor MongoDB Atlas** for storage/performance
✅ **Test database connections** on startup
✅ **Handle errors gracefully** in detection endpoints
✅ **Regular backups** of SQLite database
✅ **Index frequently queried fields** in MongoDB

---

**Ready to integrate? Follow INTEGRATION_EXAMPLES.md for code patterns!**
