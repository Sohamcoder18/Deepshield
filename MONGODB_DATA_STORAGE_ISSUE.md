# MongoDB Data Storage Troubleshooting Guide

## Issue
User data is not being stored in MongoDB during signup, so the profile page shows only the email with "-" for other fields.

## Root Cause
MongoDB connection might be failing, or data isn't being committed to the database.

## Solution Steps

### Step 1: Restart Backend with New Logging
```bash
# Stop the current backend (Ctrl+C if running)
# Then restart with:
cd d:\hackethon\backend
python app.py
```

**Watch for these messages in console:**
```
✓ MongoDB Connection: SUCCESS
or
✗ MongoDB Connection Failed: [error message]
```

If you see **✗ MongoDB Connection Failed**, the MongoDB Atlas cluster might be:
- Down for maintenance
- Network access not allowed
- Credentials wrong
- Connection string invalid

### Step 2: Check What Happens During Signup

When you sign up, the backend console should show:

```
[SIGNUP] Received data - Email: test@gmail.com, Name: John Doe, Phone: +123456, Country: USA
[SIGNUP] MongoDB connection status: True
[SIGNUP] User data to store: {...}
[SIGNUP] Data stored successfully. Document ID: ObjectId('...')
[SIGNUP] User created successfully: test@gmail.com
```

If you see `MongoDB connection status: False`, then **MongoDB is not connected**.

### Step 3: Check What Happens When Viewing Profile

When you go to the profile page, the backend console should show:

```
[GET_PROFILE] Fetching profile for: test@gmail.com
[GET_PROFILE] MongoDB connection status: True
[GET_PROFILE] User found: True
[GET_PROFILE] User data: {'email': 'test@gmail.com', 'full_name': 'John Doe', ...}
```

### Step 4: If Data Still Not Showing

**Issue A: MongoDB Not Connected**
- Restart the backend
- Check MongoDB connection message
- If fails, the MongoDB URI might be wrong or MongoDB Atlas is down

**Issue B: Data Not Stored But No Error**
- Check the `[SIGNUP]` log messages
- Look for "Document ID" confirmation
- If no Document ID, check MongoDB Atlas directly

**Issue C: Data Stored But Not Retrieved**
- Check the `[GET_PROFILE]` log messages
- Look for "User found: True"
- If "User found: False", data wasn't actually saved

## Direct MongoDB Verification

### Option 1: MongoDB Atlas Console
1. Go to https://cloud.mongodb.com/
2. Log in with your account
3. Navigate to deepfakedatabase → users collection
4. Should see user documents with all fields (full_name, phone_number, etc.)

### Option 2: MongoDB Compass (Local Tool)
1. Install MongoDB Compass
2. Connect with: mongodb+srv://sunnyrpatil18_db_user:RRLTWlNKx1LxviYk@deepfakedatabase.v3jt6zd.mongodb.net/deepfakedatabase
3. Check users collection
4. Should see all user data

## What Each Log Message Means

| Log Message | Meaning | Action |
|---|---|---|
| `✓ MongoDB Connection: SUCCESS` | MongoDB is connected | Good! Continue |
| `✗ MongoDB Connection Failed: ...` | Can't connect to MongoDB | Check credentials/network |
| `[SIGNUP] MongoDB connection status: True` | Ready to store data | Good! Continue |
| `[SIGNUP] Data stored successfully. Document ID: ...` | Data was saved | Perfect! |
| `[SIGNUP] Database error: ...` | Error during save | Check MongoDB Atlas |
| `[GET_PROFILE] User found: True` | Data retrieved from DB | Good! Should display |
| `[GET_PROFILE] User found: False` | User not in database | Data wasn't stored |
| `[GET_PROFILE] MongoDB is not connected!` | Can't access MongoDB | Restart backend |

## Quick Test Checklist

- [ ] Backend restarted after changes
- [ ] MongoDB connection message shows SUCCESS
- [ ] Sign up with complete profile data
- [ ] Check backend logs for `[SIGNUP] Data stored successfully`
- [ ] Go to profile page
- [ ] Check backend logs for `[GET_PROFILE] User found: True`
- [ ] Profile page should show all data
- [ ] Check MongoDB Atlas to see data (optional)

## If It Still Doesn't Work

1. **Copy the exact error messages** from the backend console
2. Share them so we can diagnose the issue
3. Common problems:
   - Network timeout connecting to MongoDB Atlas
   - Invalid MongoDB credentials in .env
   - MongoDB Atlas IP whitelist blocking your connection
   - MongoDB cluster is paused

## Advanced: Check MongoDB Atlas Status

1. Log in to MongoDB Atlas: https://cloud.mongodb.com/
2. Go to Database → Clusters
3. Check if "deepfakedatabase" cluster is RUNNING (not paused)
4. If paused, click "Resume" to start it

## MongoDB URI Breakdown

The connection string in `.env`:
```
mongodb+srv://sunnyrpatil18_db_user:RRLTWlNKx1LxviYk@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

- `sunnyrpatil18_db_user` - Username
- `RRLTWlNKx1LxviYk` - Password
- `deepfakedatabase.v3jt6zd.mongodb.net` - Cluster URL
- `deepfakedatabase` - Database name

If any of these are wrong, connection fails.

## Next Steps

1. **Restart backend** with: `python app.py`
2. **Watch console** for connection status
3. **Sign up again** with complete data
4. **Check backend logs** during signup
5. **Go to profile** and check logs again
6. **Report any error messages** you see

The enhanced logging will show exactly where the data flow is breaking down!
