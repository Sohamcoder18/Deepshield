# System Architecture Diagram

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEEPFAKE DETECTION SYSTEM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │              FLASK BACKEND (app.py)                      │   │
│   │                                                           │   │
│   │  ┌────────────────────────────────────────────────────┐  │   │
│   │  │  Detection Endpoints                               │  │   │
│   │  │  - /api/analyze/image                              │  │   │
│   │  │  - /api/analyze/video                              │  │   │
│   │  │  - /api/analyze/audio                              │  │   │
│   │  │  - /api/fusion/combine                             │  │   │
│   │  └────────────────────────────────────────────────────┘  │   │
│   │                          ↓                                 │   │
│   │  ┌────────────────────────────────────────────────────┐  │   │
│   │  │  Detection Models                                  │  │   │
│   │  │  - ImageDetector (XceptionNet)                    │  │   │
│   │  │  - VideoDetector (Frame analysis)                 │  │   │
│   │  │  - AudioDetector (MFCC analysis)                  │  │   │
│   │  │  - FusionLogic (Weighted combination)             │  │   │
│   │  └────────────────────────────────────────────────────┘  │   │
│   │                          ↓                                 │   │
│   │  ┌────────────────────────────────────────────────────┐  │   │
│   │  │  Database Manager                                  │  │   │
│   │  │  (utils/database_utils.py)                         │  │   │
│   │  └────────────────────────────────────────────────────┘  │   │
│   │                     ↙              ↘                       │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                        ↓                  ↓                         │
│   ┌─────────────────────────┐  ┌──────────────────────────────┐   │
│   │    SQLite Database       │  │   MongoDB Database            │   │
│   │                          │  │                               │   │
│   │ deepfake_detection.db    │  │ deepfakedatabase (Cloud)      │   │
│   │                          │  │                               │   │
│   │ Tables:                  │  │ Collections:                  │   │
│   │ - analysis_results       │  │ - analysis_results            │   │
│   │ - users                  │  │ - users                       │   │
│   │                          │  │ - fusion_results              │   │
│   │ (Local File-based)       │  │ - audit_logs                  │   │
│   │                          │  │                               │   │
│   │ Connection: Direct       │  │ Connection String:            │   │
│   │ Location: ./backend/     │  │ mongodb+srv://...             │   │
│   └─────────────────────────┘  └──────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## API Endpoints Architecture

```
┌─────────────────────────────────────────────────────────────┐
│             API ENDPOINTS & DATA FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Image/Video/Audio Analysis                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ POST /api/analyze/image                              │   │
│  │ POST /api/analyze/video                              │   │
│  │ POST /api/analyze/audio                              │   │
│  │            ↓                                          │   │
│  │  Detection Process                                   │   │
│  │            ↓                                          │   │
│  │  Save Results (NEW)                                  │   │
│  │            ↓                                          │   │
│  │  Return with analysis_id                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Database Operations (NEW)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ POST /api/results/save                               │   │
│  │ GET  /api/results/{analysis_id}                      │   │
│  │ GET  /api/results                                    │   │
│  │ GET  /api/db/status                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Fusion Analysis                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ POST /api/fusion/combine                             │   │
│  │            ↓                                          │   │
│  │  Save Fusion Result (NEW)                            │   │
│  │            ↓                                          │   │
│  │  Return fusion_id                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow for Analysis with Database Saving

```
┌─────────────────────────────────────────────────────────────────┐
│  CLIENT REQUEST (File upload)                                    │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  VALIDATION & FILE HANDLING                                      │
│  - Check file exists & format                                    │
│  - Save to uploads/ folder                                       │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  DETECTION PROCESSING                                            │
│  - Image: XceptionNet                                            │
│  - Video: Frame-by-frame analysis                                │
│  - Audio: MFCC extraction                                        │
│  Result: {trust_score, is_fake, confidence, etc.}                │
└────────────────────────────┬──────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  DATABASE SAVING (NEW)                                           │
│  - Generate analysis_id (UUID)                                   │
│  - Create analysis_data dict                                     │
│  - Call db_manager.save_analysis_result()                        │
└────────────────────┬─────────────────────┬───────────────────────┘
                     │                     │
                ╔════╨════╗           ╔════╨════╗
                ║ SQLite  ║           ║ MongoDB ║
                ║ Storage ║           ║ Storage ║
                ║ (Local) ║           ║ (Cloud) ║
                ╚════════╝           ╚════════╝
                     │                     │
                     └─────────┬───────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│  RESPONSE TO CLIENT                                              │
│  {                                                                │
│    status: "success",                                             │
│    analysis_id: "uuid-here",                                     │
│    sqlite_id: 1,                                                 │
│    mongodb_id: "objectid-here",                                  │
│    trust_score: 85.5,                                            │
│    ...                                                            │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  CLEANUP                                                         │
│  - Delete uploaded file from uploads/                            │
│  - Log completion                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Database Manager Architecture

```
┌──────────────────────────────────────────────────────┐
│        DatabaseManager (database_utils.py)           │
├──────────────────────────────────────────────────────┤
│                                                       │
│  __init__(sqlite_db, mongo_db)                       │
│       ↓                                               │
│  ┌────────────────────────────────────────────────┐  │
│  │  Public Methods:                               │  │
│  │  - save_analysis_result()                      │  │
│  │  - get_analysis_result()                       │  │
│  │  - get_all_results()                           │  │
│  │  - save_fusion_result()                        │  │
│  │  - save_audit_log()                            │  │
│  └────────────────────────────────────────────────┘  │
│                ↓                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Internal Operations:                          │  │
│  │  - Connect to SQLite via SQLAlchemy            │  │
│  │  - Connect to MongoDB via PyMongo              │  │
│  │  - Handle errors gracefully                    │  │
│  │  - Generate UUIDs                              │  │
│  │  - Timestamp management                        │  │
│  └────────────────────────────────────────────────┘  │
│                ↓                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Return Results:                               │  │
│  │  {                                              │  │
│  │    success: bool,                              │  │
│  │    sqlite_id: int,                             │  │
│  │    mongodb_id: str,                            │  │
│  │    errors: list                                │  │
│  │  }                                              │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## File Structure

```
backend/
├── app.py                          # Main Flask app (UPDATED)
├── requirements.txt                # Dependencies (UPDATED)
├── .env                            # Environment config (NEW - CRITICAL)
├── deepfake_detection.db           # SQLite database (auto-created)
│
├── models/
│   ├── __init__.py
│   ├── image_detector.py
│   ├── video_detector.py
│   ├── audio_detector.py
│   ├── fusion_logic.py
│   └── database_models.py          # SQLite models (NEW)
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── validators.py
│   └── database_utils.py           # Database Manager (NEW)
│
├── uploads/                        # Temporary file storage
│
└── Documentation/                  # Documentation files (NEW)
    ├── DATABASE_SETUP.md
    ├── DATABASE_SUMMARY.md
    ├── QUICKSTART_DB.md
    ├── INTEGRATION_EXAMPLES.md
    └── ARCHITECTURE.md (this file)
```

## Configuration Flow

```
┌──────────────────────────────┐
│  System Startup              │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│  Load .env file              │
│  (load_dotenv())             │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│  Initialize Flask App        │
└──────────────┬───────────────┘
               │
               ↓
     ┌─────────┴──────────┐
     ↓                    ↓
SQLite Setup         MongoDB Setup
     │                    │
     ↓                    ↓
Configure URI        Connect & Verify
Create ORM           Handle failures
Create Tables        Log status
     │                    │
     └─────────┬──────────┘
               │
               ↓
┌──────────────────────────────┐
│  Initialize DatabaseManager  │
│  db_manager = DatabaseManager│
│  (sqlite_db=db,              │
│   mongo_db=mongo_db)         │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│  System Ready                │
│  All endpoints functional    │
└──────────────────────────────┘
```
