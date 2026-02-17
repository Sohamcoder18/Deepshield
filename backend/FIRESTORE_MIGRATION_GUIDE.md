# Firestore Migration Guide - Complete Implementation

## Overview
This document outlines the complete migration from MongoDB to Firestore database with SQLite as a backup. The migration includes proper data organization in Firestore collections and SQLite tables with date-based document IDs for easy tracking.

## Database Architecture

### Primary Database: Firestore
Firebase Firestore is used as the primary cloud database with the following collections:

### Secondary Database: SQLite
SQLite is used for local backup and offline capability with identical data structure.

---

## 1. Users Collection

### Firestore Path
```
/users/{user_email}
```

### Document ID
- **Format**: User's email address (e.g., `user@example.com`)
- **Why**: Email is unique and serves as a natural identifier
- **Benefit**: Easy lookup and referencing

### Fields
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-15",
  "country": "USA",
  "occupation": "Software Engineer",
  "created_at": "2026-02-16T10:30:00Z",
  "last_login": "2026-02-16T15:45:00Z",
  "total_analyses": 42,
  "updated_at": "2026-02-16T15:45:00Z"
}
```

### SQLite Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR(120) UNIQUE NOT NULL,
  full_name VARCHAR(120),
  phone_number VARCHAR(20),
  date_of_birth VARCHAR(20),
  country VARCHAR(50),
  occupation VARCHAR(100),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  total_analyses INTEGER DEFAULT 0,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Sub-collection: analysis_logs

Under each user document, there's a sub-collection for tracking all analyses:

```
/users/{user_email}/analysis_logs/{doc_id}
```

#### Document ID
- **Format**: `anl_YYYY-MM-DD_HH-MM-SS_uid`
- **Example**: `anl_2026-02-16_15-30-45_a1b2c3d4`
- **Why**: Date-based prefix allows developers to see when analysis was performed

#### Fields
```json
{
  "analysis_id": "analysis_2026-02-16_15-30-45_x1y2z3w4",
  "analysis_type": "image|video|audio",
  "file_name": "deepfake_video.mp4",
  "is_fake": true,
  "confidence": 92.5,
  "trust_score": 8.5,
  "timestamp": "2026-02-16T15:30:45Z"
}
```

---

## 2. Signup History Collection

### Firestore Path
```
/signup_history/{doc_id}
```

### Document ID
- **Format**: `signup_YYYY-MM-DD_HH-MM-SS_uid`
- **Example**: `signup_2026-02-16_10-15-30_abc123def`
- **Why**: Developers can quickly identify signup times by looking at document IDs

### Fields
```json
{
  "email": "newuser@example.com",
  "full_name": "Jane Smith",
  "phone_number": "+1987654321",
  "date_of_birth": "1995-06-20",
  "country": "UK",
  "occupation": "Data Scientist",
  "timestamp": "2026-02-16T10:15:30Z",
  "event_type": "signup",
  "status": "success"
}
```

### Use Cases
- Track user registrations over time
- Analyze signup trends by date
- Find all signups on a specific date

### SQLite Table
```sql
CREATE TABLE signup_history (
  id INTEGER PRIMARY KEY,
  email VARCHAR(120) NOT NULL,
  full_name VARCHAR(120),
  phone_number VARCHAR(20),
  date_of_birth VARCHAR(20),
  country VARCHAR(50),
  occupation VARCHAR(100),
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  event_type VARCHAR(20) DEFAULT 'signup',
  status VARCHAR(20) DEFAULT 'success'
);
```

---

## 3. Login History Collection

### Firestore Path
```
/login_history/{doc_id}
```

### Document ID
- **Format**: `login_YYYY-MM-DD_HH-MM-SS_uid`
- **Example**: `login_2026-02-16_14-45-20_xyz789abc`
- **Why**: Quick date identification for when users logged in

### Fields
```json
{
  "email": "user@example.com",
  "timestamp": "2026-02-16T14:45:20Z",
  "event_type": "login",
  "status": "success",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### Use Cases
- Track user login patterns
- Identify suspicious login attempts
- Analyze access patterns by date and time
- User activity monitoring

### SQLite Table
```sql
CREATE TABLE login_history (
  id INTEGER PRIMARY KEY,
  email VARCHAR(120) NOT NULL,
  ip_address VARCHAR(50),
  user_agent VARCHAR(500),
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  event_type VARCHAR(20) DEFAULT 'login',
  status VARCHAR(20) DEFAULT 'success'
);
```

---

## 4. Analysis Results Collection

### Firestore Path
```
/analysis_results/{doc_id}
```

### Document ID
- **Format**: `analysis_YYYY-MM-DD_HH-MM-SS_uid`
- **Example**: `analysis_2026-02-16_15-30-45_a1b2c3d4`
- **Why**: Developers can identify when analysis was performed just by looking at the ID

### Fields
```json
{
  "user_email": "user@example.com",
  "analysis_type": "image|video|audio",
  "file_name": "sample_video.mp4",
  "file_size": 5242880,
  "trust_score": 75.5,
  "is_fake": true,
  "confidence": 92.0,
  "recommendation": "This content appears to be a deepfake",
  "analysis_time": 5.234,
  "timestamp": "2026-02-16T15:30:45Z",
  "xception_score": 0.92,
  "artifact_detection": 0.85,
  "synthesis_probability": 0.88,
  "spectral_consistency": 0.91,
  "temporal_consistency": 0.89
}
```

### Use Cases
- Store all deepfake analysis results
- Historical record of all analysis performed
- User can query their own analyses
- System-wide analysis trends

### SQLite Table
```sql
CREATE TABLE analysis_results (
  id INTEGER PRIMARY KEY,
  analysis_id VARCHAR(100) UNIQUE NOT NULL,
  user_email VARCHAR(120),
  analysis_type VARCHAR(20) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_size INTEGER,
  trust_score FLOAT,
  is_fake BOOLEAN,
  confidence FLOAT,
  recommendation TEXT,
  analysis_time FLOAT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ID Generation Strategy

All date-based IDs follow the pattern:
```
{prefix}_YYYY-MM-DD_HH-MM-SS_{unique_id}
```

### Examples
- Signup: `signup_2026-02-16_10-15-30_abc123`
- Login: `login_2026-02-16_14-45-20_def456`
- Analysis: `analysis_2026-02-16_15-30-45_ghi789`
- User Analysis Log: `anl_2026-02-16_15-30-45_jkl012`

### Benefits
1. **Date Visibility**: Developers can immediately see when events occurred
2. **Temporal Sorting**: Documents naturally sort by date/time
3. **Unique Identification**: 8-character unique suffix prevents collisions
4. **Easy Filtering**: Can query by date prefix
5. **Human-Readable**: Non-cryptic IDs that maintenance developers can understand

---

## API Changes

### Authentication Endpoints

#### Signup
```
POST /api/auth/signup
```
**Changes**: Now saves signup event to `signup_history` collection AND user profile to `users` collection

#### Login
```
POST /api/auth/login
```
**Changes**: Now saves login event to `login_history` collection with IP and user agent

#### Get User Profile
```
GET /api/auth/user
```
**Data Source**: Firestore `users/{email}` document first, SQLite backup second

#### Update Profile
```
POST /api/auth/update-profile
```
**Behavior**: Updates `users/{email}` document in Firestore and SQLite

### Analysis Endpoints

#### Image Analysis
```
POST /api/analyze/image
```
**Changes**: 
- Saves to `analysis_results` collection
- Saves to user's `analysis_logs` sub-collection
- Document ID: `analysis_YYYY-MM-DD_HH-MM-SS_uid`

#### Video Analysis
```
POST /api/analyze/video
```
**Changes**: 
- Saves to `analysis_results` collection
- Saves to user's `analysis_logs` sub-collection
- Document ID: `analysis_YYYY-MM-DD_HH-MM-SS_uid`

#### Audio Analysis
```
POST /api/analyze/audio
```
**Changes**: 
- Saves to `analysis_results` collection
- Saves to user's `analysis_logs` sub-collection
- Document ID: `analysis_YYYY-MM-DD_HH-MM-SS_uid`

### Query Endpoints

#### Get Single Result
```
GET /api/results/{analysis_id}
```
**Data Source**: Firestore `analysis_results` collection first, SQLite backup second

#### Get All Results
```
GET /api/results?limit=100&user_email=user@example.com
```
**Data Source**: Firestore `analysis_results` (filtered), SQLite backup second

---

## Firestore Manager API

### Methods

#### `firestore_manager.save_signup_event(email, user_data)`
Saves signup event to `signup_history` collection

#### `firestore_manager.save_login_event(email, additional_data)`
Saves login event to `login_history` collection

#### `firestore_manager.save_analysis_result(analysis_data)`
Saves analysis to `analysis_results` collection

#### `firestore_manager.save_user_profile(email, user_data)`
Saves/updates user profile in `users` collection

#### `firestore_manager.save_user_analysis_log(email, analysis_id, analysis_data)`
Saves analysis to user's `analysis_logs` sub-collection

#### `firestore_manager.get_user_profile(email)`
Retrieves user profile from `users` collection

#### `firestore_manager.get_user_analysis_logs(email, limit=50)`
Retrieves user's analysis history from sub-collection

#### `firestore_manager.update_last_login(email)`
Updates user's `last_login` timestamp

#### `firestore_manager.get_login_history(user_email=None, limit=100)`
Retrieves login history records

#### `firestore_manager.get_signup_history(limit=100)` 
Retrieves signup history records

#### `firestore_manager.get_analysis_history(user_email=None, limit=100)`
Retrieves analysis history

---

## Configuration

### Environment Variables

```env
# Firebase credentials (option 1: JSON path)
FIREBASE_CREDENTIALS_PATH=database_info.json

# OR (option 2: JSON string in env variable)
FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### Credentials File Format
The `database_info.json` should be a Firebase service account JSON file:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-...@...iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## Data Flow Diagram

```
User Registration (Signup)
    ↓
[OTP Verification]
    ↓
┌─────────────────────────┐
│   Save to Firestore     │
├─────────────────────────┤
│ 1. users/{email}        │
│ 2. signup_history/*     │
└─────────────────────────┘
    ↓ (Backup)
┌─────────────────────────┐
│   Save to SQLite        │
├─────────────────────────┤
│ 1. users table          │
│ 2. signup_history table │
└─────────────────────────┘
    ↓
[Registration Complete]

---

User Login
    ↓
[OTP Verification]
    ↓
┌─────────────────────────┐
│   Save to Firestore     │
├─────────────────────────┤
│ 1. login_history/*      │
│ 2. Update users/{email} │
└─────────────────────────┘
    ↓ (Backup)
┌─────────────────────────┐
│   Update in SQLite      │
├─────────────────────────┤
│ 1. login_history table  │
│ 2. users table          │
└─────────────────────────┘
    ↓
[Send JWT Token]

---

File Analysis
    ↓
[Detect Deepfake]
    ↓
┌─────────────────────────┐
│   Save to Firestore     │
├─────────────────────────┤
│ 1. analysis_results/*   │
│ 2. users/{email}/       │
│    analysis_logs/*      │
└─────────────────────────┘
    ↓ (Backup)
┌─────────────────────────┐
│   Save to SQLite        │
├─────────────────────────┤
│ 1. analysis_results     │
│    table                │
└─────────────────────────┘
    ↓
[Return Results]
```

---

## Migration Checklist

- ✅ Replace `pymongo` with `firebase-admin` in requirements.txt
- ✅ Remove MongoDB connection code from app.py
- ✅ Create `FirestoreManager` utility class
- ✅ Update authentication endpoints (signup, login)
- ✅ Update analysis endpoints (image, video, audio)
- ✅ Update results endpoints (get/save)
- ✅ Create SQLite backup tables (signup_history, login_history)
- ✅ Update database models
- ✅ Implement date-based document IDs
- ✅ Separate data fields (login/signup/analysis all in different collections)

---

## Benefits of This Architecture

1. **Firestore (Primary)**
   - Cloud-hosted, globally distributed
   - Real-time database updates
   - Automatic backup and recovery
   - Scalable NoSQL structure
   - Sub-collections for hierarchical data

2. **SQLite (Backup)**
   - Local offline storage
   - No internet required for backup
   - Fast local access
   - Data persistence
   - Emergency fallback

3. **Separation of Concerns**
   - Signup data isolated in `signup_history`
   - Login data isolated in `login_history`
   - Analysis data isolated in `analysis_results`
   - User profiles in `users`
   - User-specific analysis logs in sub-collections

4. **Date-Based IDs**
   - Human-readable document IDs
   - Easy temporal filtering
   - Natural sorting by time
   - Developer-friendly tracking
   - Audit trail visibility

---

## Troubleshooting

### Firestore Connection Issues
1. Check Firebase credentials in `database_info.json`
2. Ensure Firebase project has Firestore database enabled
3. Check network connectivity
4. SQLite backup will be used automatically

### Missing Data
1. Check both Firestore and SQLite
2. Verify document IDs match expected format
3. Check Firestore indexes if using complex queries

### Performance Issues
1. Use appropriate document limits in queries
2. Create Firestore composite indexes for common queries
3. Monitor Firestore read/write usage in Firebase Console

---

## Future Enhancements

1. **Firestore Indexes**: Create composite indexes for complex queries
2. **Real-time Sync**: Implement real-time listeners for live updates
3. **Archive Strategy**: Move old analysis to archive collection
4. **Caching**: Implement client-side caching of frequent queries
5. **Analytics**: Use Firestore analytics for usage insights

---

## Support

For questions or issues with the migration, refer to:
- Firestore Documentation: https://firebase.google.com/docs/firestore
- Firebase Admin SDK: https://firebase.google.com/docs/admin/setup
- Database Utilities: `backend/utils/firestore_utils.py`
