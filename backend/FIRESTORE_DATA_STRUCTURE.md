# Firestore Data Structure - Quick Reference

## Collections Overview

### 🧑 `users` Collection
**Primary Database**: User profiles
**Document ID**: `{user_email}`

```
users/
├── user1@example.com/
│   ├── email: "user1@example.com"
│   ├── full_name: "John Doe"
│   ├── country: "USA"
│   ├── created_at: 2026-02-16T10:00:00Z
│   ├── last_login: 2026-02-16T15:45:00Z
│   ├── total_analyses: 42
│   └── analysis_logs/ (subcollection)
│       ├── anl_2026-02-16_15-30-45_a1b2c3d4/
│       ├── anl_2026-02-16_14-20-15_x1y2z3w4/
│       └── ...
└── user2@example.com/
    └── ...
```

### 📝 `signup_history` Collection
**Signup Events Tracking**
**Document ID**: `signup_YYYY-MM-DD_HH-MM-SS_{uid}`

```
signup_history/
├── signup_2026-02-16_10-15-30_abc123/
│   ├── email: "newuser@example.com"
│   ├── full_name: "Jane Smith"
│   ├── country: "UK"
│   ├── timestamp: 2026-02-16T10:15:30Z
│   ├── event_type: "signup"
│   └── status: "success"
│
├── signup_2026-02-16_09-45-20_def456/
│   └── ...
│
└── signup_2026-02-15_18-30-00_ghi789/
    └── ...
```

**Purpose**: 
- Track all user registrations
- Analyze signup trends
- Audit trail for new accounts
- Marketing/retention analytics

### 🔐 `login_history` Collection
**Login Events Tracking**
**Document ID**: `login_YYYY-MM-DD_HH-MM-SS_{uid}`

```
login_history/
├── login_2026-02-16_14-45-20_jkl012/
│   ├── email: "user@example.com"
│   ├── ip_address: "192.168.1.100"
│   ├── user_agent: "Mozilla/5.0..."
│   ├── timestamp: 2026-02-16T14:45:20Z
│   ├── event_type: "login"
│   └── status: "success"
│
├── login_2026-02-16_10-30-15_mno345/
│   └── ...
│
└── login_2026-02-15_22-15-00_pqr678/
    └── ...
```

**Purpose**:
- Track user access patterns
- Detect suspicious logins
- Security monitoring
- Usage analytics

### 📊 `analysis_results` Collection
**All Deepfake Analysis Results**
**Document ID**: `analysis_YYYY-MM-DD_HH-MM-SS_{uid}`

```
analysis_results/
├── analysis_2026-02-16_15-30-45_stu901/
│   ├── user_email: "user@example.com"
│   ├── analysis_type: "image"
│   ├── file_name: "deepfake.jpg"
│   ├── file_size: 2048576
│   ├── trust_score: 75.5
│   ├── is_fake: true
│   ├── confidence: 92.0
│   ├── recommendation: "Content appears suspicious"
│   ├── analysis_time: 5.234
│   ├── timestamp: 2026-02-16T15:30:45Z
│   ├── xception_score: 0.92
│   ├── artifact_detection: 0.85
│   └── ...
│
├── analysis_2026-02-16_14-20-15_vwx234/
│   ├── user_email: "user2@example.com"
│   ├── analysis_type: "video"
│   ├── duration: 45.3
│   ├── frames_analyzed: 15
│   └── ...
│
└── analysis_2026-02-16_13-10-00_yza567/
    ├── user_email: "user3@example.com"
    ├── analysis_type: "audio"
    ├── synthesis_probability: 0.88
    └── ...
```

**Purpose**:
- Central analysis result repository
- Historical record of all detections
- System-wide statistics
- Research and audit

---

## ID Format Pattern

### Date-Based Document IDs
All documents follow the pattern:
```
{event_type}_YYYY-MM-DD_HH-MM-SS_{unique_id}
```

### Examples
- **Signup**: `signup_2026-02-16_10-15-30_abc123`
- **Login**: `login_2026-02-16_14-45-20_jkl012`
- **Analysis**: `analysis_2026-02-16_15-30-45_stu901`
- **User Analysis Log**: `anl_2026-02-16_15-30-45_a1b2c3d4`

### Benefits
✅ **human-read able** - See event type at a glance
✅ **Date visible** - Know exactly when event occurred  
✅ **Auto-sorted** - Documents naturally sort chronologically
✅ **Filterable** - Query by date prefix easily
✅ **Unique** - Hash suffix prevents collisions

---

## Common Queries

### Find all signups on a specific date
```javascript
db.collection('signup_history')
  .where('timestamp', '>=', new Date('2026-02-16'))
  .where('timestamp', '<', new Date('2026-02-17'))
  .orderBy('timestamp', 'desc')
  .get()
```

### Find all logins for a user
```javascript
db.collection('login_history')
  .where('email', '==', 'user@example.com')
  .orderBy('timestamp', 'desc')
  .limit(50)
  .get()
```

### Get user's analysis history
```javascript
db.collection('users')
  .doc('user@example.com')
  .collection('analysis_logs')
  .orderBy('timestamp', 'desc')
  .limit(20)
  .get()
```

### Find all analyses from last 24 hours
```javascript
const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000);
db.collection('analysis_results')
  .where('timestamp', '>=', yesterday)
  .orderBy('timestamp', 'desc')
  .get()
```

### Find all fake detections with high confidence
```javascript
db.collection('analysis_results')
  .where('is_fake', '==', true)
  .where('confidence', '>=', 90)
  .orderBy('confidence', 'desc')
  .get()
```

---

## Data Separation Strategy

### Why Separate Collections?

| Data Type | Collection | Document ID | Purpose |
|-----------|-----------|------------|---------|
| User Profiles | `users` | Email | Single source of truth for user data |
| Signups | `signup_history` | Date-based | Track registration events |
| Logins | `login_history` | Date-based | Audit login activity |
| Analysis | `analysis_results` | Date-based | Store all detection results |
| User's Analyses | Sub-collection | Date-based | Fast user-specific queries |

### Querying Benefits
- **Fast lookups**: Direct email access for user profiles
- **Date filtering**: Easy temporal analysis of events
- **Segregation**: Each data type has its own collection
- **Scalability**: Not mixing unrelated data
- **Security**: Can set different access rules per collection
- **Performance**: Smaller, focused collections query faster

---

## SQLite Backup Tables

All Firestore collections have corresponding SQLite tables:

```sql
-- User profiles
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  email VARCHAR UNIQUE,
  full_name VARCHAR,
  created_at DATETIME,
  last_login DATETIME,
  total_analyses INTEGER
);

-- Signup events
CREATE TABLE signup_history (
  id INTEGER PRIMARY KEY,
  email VARCHAR,
  full_name VARCHAR,
  timestamp DATETIME,
  event_type VARCHAR,
  status VARCHAR
);

-- Login events
CREATE TABLE login_history (
  id INTEGER PRIMARY KEY,
  email VARCHAR,
  ip_address VARCHAR,
  user_agent VARCHAR,
  timestamp DATETIME,
  event_type VARCHAR,
  status VARCHAR
);

-- Analysis results
CREATE TABLE analysis_results (
  id INTEGER PRIMARY KEY,
  analysis_id VARCHAR UNIQUE,
  user_email VARCHAR,
  analysis_type VARCHAR,
  file_name VARCHAR,
  trust_score FLOAT,
  is_fake BOOLEAN,
  confidence FLOAT,
  timestamp DATETIME
);
```

---

## Data Flow Example

### User Signup Flow
```
1. User submits signup form
   ↓
2. OTP verified
   ↓
3. Save to Firestore:
   - Create document: /users/{email}
   - Create document: /signup_history/{signup_date_id}
   ↓
4. Backup to SQLite:
   - Insert row in users table
   - Insert row in signup_history table
   ↓
5. Return success to client
```

### File Analysis Flow
```
1. User uploads file
   ↓
2. Run deepfake detection
   ↓
3. Save to Firestore:
   - Create document: /analysis_results/{analysis_date_id}
   - Create sub-doc: /users/{email}/analysis_logs/{anl_date_id}
   ↓
4. Backup to SQLite:
   - Insert row in analysis_results table
   ↓
5. Return results to client
```

---

## Monitoring & Debugging

### Check Firestore Status
```python
# In Flask shell
from utils.firestore_utils import FirestoreManager
fm = FirestoreManager('database_info.json')
print(f"Firestore available: {fm.firestore_available}")
```

### View Collections
1. Open [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Firestore Database
4. See all collections listed

### Check SQLite Backup
```python
from models.database_models import User, LoginHistory, SignupHistory, AnalysisResult

# Count users
print(f"Users: {User.query.count()}")

# Count logins today
today = datetime.utcnow().date()
print(f"Logins today: {LoginHistory.query.filter(LoginHistory.timestamp >= today).count()}")

# Count analyses
print(f"Total analyses: {AnalysisResult.query.count()}")
```

### Troubleshooting
1. **No Firestore data?** → Check Firebase credentials
2. **Only SQLite data?** → Firestore may be offline (temporary - will reconnect)
3. **Mismatch between DBs?** → Run data sync process
4. **Document IDs wrong?** → Check timestamp format

---

## Best Practices

### ✅ DO
- Use date-based IDs for temporal analysis
- Separate events into different collections
- Query Firestore first, then SQLite
- Create composite indexes for complex queries
- Monitor Firestore quota usage

### ❌ DON'T
- Don't mix data types in single collection
- Don't use random UUIDs as document IDs (use date format)
- Don't rely on Firestore alone (keep SQLite backup)
- Don't create large nested documents (use subcollections)
- Don't ignore sync errors between databases

---

## Quick Stats

**Collections**: 4
- `users`
- `signup_history`
- `login_history`
- `analysis_results`

**Sub-collections**: 1
- `users/{email}/analysis_logs`

**SQLite Tables**: 4
- `users`
- `signup_history`
- `login_history`
- `analysis_results`

**Total Possible Documents** (no limit in Firestore):
- Users: Unlimited
- Signups: 1 per registration
- Logins: 1 per login
- Analyses: 1 per file analyzed
- User Analysis Logs: 1 per user analysis

---

## Integration Points

### Backend
- `app.py` - Flask application
- `utils/firestore_utils.py` - Database management
- `models/database_models.py` - SQLite schema

### Frontend
- All existing APIs remain compatible
- Response format unchanged
- Only database changed (transparent to frontend)

### Third-party Services
- Firebase Firestore (cloud)
- SQLite (local)
- Brevo (email notifications)
- Groq (AI assistant)

---

## Documentation Links

- [Complete Migration Guide](FIRESTORE_MIGRATION_GUIDE.md)
- [Migration Summary](FIRESTORE_MIGRATION_COMPLETE.md)
- [Firebase Firestore Docs](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)

---

**Last Updated**: 2026-02-16  
**Status**: ✅ Production Ready  
**Backup**: ✅ SQLite Enabled  
**Cloud**: ✅ Firestore Connected
