# Database Setup Guide - DeepFake Detection System

This document explains how to set up and use both SQLite and MongoDB databases with the DeepFake Detection backend.

## Overview

The system supports two databases:
- **SQLite**: Local file-based database (ideal for development and testing)
- **MongoDB**: Cloud-based NoSQL database (ideal for production and scalability)

## Installation

### 1. Install Required Packages

```bash
cd backend
pip install -r requirements.txt
```

The following packages will be installed:
- `pymongo==3.11.4` - MongoDB driver
- `sqlalchemy==2.0.0` - SQL toolkit and ORM
- `flask-sqlalchemy==3.0.3` - Flask extension for SQLAlchemy

### 2. Environment Configuration

Create a `.env` file in the `backend` folder with your MongoDB credentials:

```bash
# .env
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:<db_password>@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
FLASK_ENV=development
FLASK_DEBUG=True
SQLALCHEMY_DATABASE_URI=sqlite:///deepfake_detection.db
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
```

**IMPORTANT**: Replace `<db_password>` with your actual MongoDB password.

## Database Structure

### SQLite

SQLite database stores data locally in `deepfake_detection.db` file.

**Tables:**
1. **analysis_results**
   - Stores detection results for images, videos, and audio
   - Fields: id, analysis_id, analysis_type, file_name, file_size, trust_score, is_fake, confidence, recommendation, analysis_time, timestamp

2. **users**
   - Stores user information
   - Fields: id, username, email, created_at, analyses_count

### MongoDB

MongoDB collections in the `deepfakedatabase`:

1. **analysis_results**
   - Stores detailed analysis results
   - Supports flexible schema for different analysis types

2. **users**
   - Stores user profiles and metadata

3. **fusion_results**
   - Stores combined analysis results from multiple detection types

4. **audit_logs**
   - Stores activity logs for compliance and debugging

## API Endpoints

### 1. Database Status
```
GET /api/db/status
```
Check the connection status of both databases.

**Response:**
```json
{
  "status": "ok",
  "databases": {
    "sqlite": "connected",
    "mongodb": "connected"
  },
  "timestamp": "2024-02-01T10:30:00"
}
```

### 2. Save Analysis Result
```
POST /api/results/save
```
Save analysis result to both databases.

**Query Parameters:**
- `use_sqlite` (default: true) - Save to SQLite
- `use_mongodb` (default: true) - Save to MongoDB

**Request Body:**
```json
{
  "analysis_type": "image",
  "file_name": "test_image.jpg",
  "file_size": 102400,
  "trust_score": 85.5,
  "is_fake": false,
  "confidence": 0.92,
  "recommendation": "authentic",
  "analysis_time": 2.34
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Result saved successfully",
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "sqlite_id": 1,
  "mongodb_id": "65b8c1a2f7e4b2c3d4e5f6g7",
  "timestamp": "2024-02-01T10:30:00"
}
```

### 3. Retrieve Analysis Result
```
GET /api/results/<analysis_id>
```
Retrieve a specific analysis result.

**Query Parameters:**
- `source` (options: sqlite, mongodb, both) - Default: both

**Response:**
```json
{
  "status": "success",
  "data": {
    "sqlite": {
      "id": 1,
      "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
      "trust_score": 85.5,
      ...
    },
    "mongodb": {
      "_id": "65b8c1a2f7e4b2c3d4e5f6g7",
      "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
      "trust_score": 85.5,
      ...
    }
  },
  "timestamp": "2024-02-01T10:30:00"
}
```

### 4. Get All Results
```
GET /api/results
```
Retrieve all analysis results.

**Query Parameters:**
- `limit` (default: 100) - Maximum number of results
- `source` (options: sqlite, mongodb, both) - Default: both

**Response:**
```json
{
  "status": "success",
  "data": {
    "sqlite": [...],
    "mongodb": [...]
  },
  "total_sqlite": 45,
  "total_mongodb": 45,
  "timestamp": "2024-02-01T10:30:00"
}
```

## Usage Examples

### Python Example
```python
import requests
import json

BASE_URL = "http://localhost:5000"

# Check database status
response = requests.get(f"{BASE_URL}/api/db/status")
print(response.json())

# Save an analysis result
result_data = {
    "analysis_type": "image",
    "file_name": "sample.jpg",
    "file_size": 50000,
    "trust_score": 78.5,
    "is_fake": True,
    "confidence": 0.85,
    "recommendation": "suspicious",
    "analysis_time": 1.5
}

response = requests.post(f"{BASE_URL}/api/results/save", json=result_data)
result = response.json()
print(f"Saved with ID: {result['analysis_id']}")

# Retrieve the result
analysis_id = result['analysis_id']
response = requests.get(f"{BASE_URL}/api/results/{analysis_id}")
print(response.json())

# Get all results
response = requests.get(f"{BASE_URL}/api/results?limit=10&source=both")
print(response.json())
```

### JavaScript/Fetch Example
```javascript
const BASE_URL = "http://localhost:5000";

// Check database status
async function checkDBStatus() {
  const response = await fetch(`${BASE_URL}/api/db/status`);
  const data = await response.json();
  console.log(data);
}

// Save analysis result
async function saveResult(resultData) {
  const response = await fetch(`${BASE_URL}/api/results/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(resultData)
  });
  const data = await response.json();
  return data;
}

// Retrieve result
async function getResult(analysisId) {
  const response = await fetch(`${BASE_URL}/api/results/${analysisId}`);
  const data = await response.json();
  return data;
}

// Get all results
async function getAllResults(limit = 10) {
  const response = await fetch(`${BASE_URL}/api/results?limit=${limit}`);
  const data = await response.json();
  return data;
}
```

## Database Synchronization

Both databases are synchronized during save operations. If you want to:

### Save to SQLite only:
```
POST /api/results/save?use_sqlite=true&use_mongodb=false
```

### Save to MongoDB only:
```
POST /api/results/save?use_sqlite=false&use_mongodb=true
```

### Retrieve from SQLite only:
```
GET /api/results/<analysis_id>?source=sqlite
```

### Retrieve from MongoDB only:
```
GET /api/results/<analysis_id>?source=mongodb
```

## Troubleshooting

### MongoDB Connection Issues
If you get a MongoDB connection error:
1. Verify the connection string in `.env`
2. Check that your IP address is whitelisted in MongoDB Atlas
3. Ensure the password is correct and URL-encoded if needed

### SQLite Issues
1. Check that `uploads` folder has write permissions
2. Delete `deepfake_detection.db` and restart the app to recreate it
3. Ensure no other process is locking the database file

### Database Initialization
The SQLAlchemy ORM automatically creates tables on first run. If you need to reset:
```python
# In Python shell or script
from app import app, db
with app.app_context():
    db.create_all()  # Create all tables
    # or
    db.drop_all()   # Drop all tables (careful!)
```

## Best Practices

1. **Use both databases** for redundancy and reliability
2. **Regular backups** of SQLite database
3. **Monitor MongoDB** Atlas for storage and performance
4. **Test database connections** on app startup
5. **Handle database errors gracefully** in your code
6. **Use appropriate indexes** in MongoDB for frequently queried fields

## Performance Considerations

- **SQLite**: Good for development, limited concurrent access
- **MongoDB**: Better for production, handles concurrent access well
- For high-volume applications, consider using both with MongoDB as primary
