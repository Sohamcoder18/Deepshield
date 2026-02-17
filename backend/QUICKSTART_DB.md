# Quick Start Guide - Database Configuration

## Step 1: Update .env File

Edit `backend/.env` and replace `<db_password>` with your actual MongoDB password:

```
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:YOUR_PASSWORD_HERE@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

## Step 2: Install Packages

```bash
cd backend
python -m pip install pymongo sqlalchemy flask-sqlalchemy
```

## Step 3: Run the Server

```bash
python app.py
```

## Step 4: Test Database Connections

Open your browser or use curl:

```bash
# Check database status
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

## Step 5: Save and Retrieve Results

### Save a result:
```bash
curl -X POST http://localhost:5000/api/results/save \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "image",
    "file_name": "test.jpg",
    "file_size": 100000,
    "trust_score": 75.5,
    "is_fake": false,
    "confidence": 0.88,
    "recommendation": "authentic",
    "analysis_time": 2.5
  }'
```

This will return an `analysis_id` that you can use to retrieve the result.

### Retrieve the result:
```bash
curl http://localhost:5000/api/results/{analysis_id}
```

### Get all results:
```bash
curl "http://localhost:5000/api/results?limit=10"
```

## Key Features

✅ **Dual Database Support**: Data saved to both SQLite and MongoDB automatically
✅ **Independent Operation**: Each database can be queried separately
✅ **Automatic Fallback**: If one database fails, the system continues with the other
✅ **Flexible Configuration**: Use query parameters to control which database to use
✅ **Complete History**: All analysis results are stored for auditing and reporting

## Database Locations

- **SQLite**: `backend/deepfake_detection.db` (local file)
- **MongoDB**: Cloud database accessible via connection string

## Files Created

1. `backend/.env` - Environment configuration (contains MongoDB credentials)
2. `backend/models/database_models.py` - SQLAlchemy models for SQLite
3. `backend/utils/database_utils.py` - Database manager utility class
4. `backend/DATABASE_SETUP.md` - Detailed setup documentation

## Next Steps

1. Integrate database saving into your detection endpoints
2. Add user authentication
3. Create dashboard to view analysis history
4. Set up automated backups for SQLite database

For detailed information, see `DATABASE_SETUP.md`.
