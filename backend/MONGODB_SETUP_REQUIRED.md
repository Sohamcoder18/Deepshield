# ⚙️ MONGODB CONNECTION SETUP - REQUIRED

## 🚨 Action Required

Your backend server needs the MongoDB password to connect to the database.

### Step 1: Get Your MongoDB Password

1. Go to: https://cloud.mongodb.com/
2. Log in with your MongoDB Atlas account
3. Find your cluster: **deepfakedatabase**
4. Click "Connect"
5. Select "Drivers" → "Python"
6. Copy the connection string that includes the password
7. **Extract just the password** from the connection string

Example:
```
mongodb+srv://sunnyrpatil18_db_user:YOUR_PASSWORD_HERE@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
                                     ^^^^^^^^^^^^^^^^
                                     This is your password
```

### Step 2: Update .env File

Edit `backend/.env` and replace `<db_password>` with your actual password:

**BEFORE:**
```env
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:<db_password>@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

**AFTER:**
```env
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:YOUR_PASSWORD@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

### Step 3: Restart Server

```bash
python app.py
```

---

## ✅ Expected Output

When MongoDB connects successfully, you should see:
```
INFO:__main__:✓ Connected to MongoDB successfully
INFO:__main__:All models initialized successfully!
INFO:werkzeug: * Running on http://127.0.0.1:5000
```

---

## ❌ If Still Not Working

### Issue: "bad auth : authentication failed"
**Solution**: 
- Verify the password is correct
- Check for special characters that need URL encoding
- Make sure IP is whitelisted in MongoDB Atlas

### Issue: "bad auth : authentication failed / AtlasError"
**Solution**:
- Log into MongoDB Atlas
- Go to: Database Deployments → deepfakedatabase → Network Access
- Add your current IP address
- Wait 1-2 minutes for changes to take effect
- Try again

### Issue: Connection timeout
**Solution**:
- Check your internet connection
- Verify firewall allows MongoDB connections (port 27017)
- Make sure MongoDB cluster is running
- Check if IP is whitelisted

---

## 🚀 Testing Connection

After updating `.env` and restarting, test with:

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

## ⚠️ IMPORTANT SECURITY NOTES

- **Never share** your MongoDB password
- **Never commit** the `.env` file to git
- Add `.env` to `.gitignore`
- Keep credentials confidential

---

## 📱 Example MongoDB Connection String

Your connection string format:
```
mongodb+srv://sunnyrpatil18_db_user:PASSWORD@deepfakedatabase.v3jt6zd.mongodb.net/?appName=deepfakedatabase
```

Parts:
- `sunnyrpatil18_db_user` - Username (fixed)
- `PASSWORD` - Your MongoDB password (⬅️ **REPLACE THIS**)
- `deepfakedatabase.v3jt6zd.mongodb.net` - Cluster URL (fixed)
- `appName=deepfakedatabase` - Database name (fixed)

---

**Once configured, run:** `python app.py`

**Then test:** `curl http://localhost:5000/api/db/status`
