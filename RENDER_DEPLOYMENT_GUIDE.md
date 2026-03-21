# RiskShield Render Deployment Guide

## Overview
This guide explains how to deploy RiskShield to Render.com with all necessary system dependencies for audio processing and ML models.

## Prerequisites
- Render.com account (free tier available)
- GitHub repository with RiskShield code
- Environment variables prepared (API keys, database URLs, etc.)

## Deployment Steps

### 1. Connect GitHub to Render
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub account if not already connected
4. Select the RiskShield repository

### 2. Configure Service Settings
The `render.yaml` file in the repository already includes:
- Python 3.11 runtime
- Automatic system dependency installation (portaudio19-dev)
- Gunicorn configuration with 4 workers
- Auto-deploy on git push

**No additional configuration needed in render.yaml** - it will auto-detect and use the file.

### 3. Set Environment Variables
In Render dashboard, navigate to **Environment** and add these variables:

**Required API Keys:**
```
GROQ_API_KEY=<your-groq-api-key>
BREVO_API_KEY=<your-brevo-api-key>
```

**Database Configuration (choose ONE):**

**Option A: PostgreSQL**
```
DATABASE_URL=postgresql://user:password@host:5432/riskshield
```

**Option B: Firebase/Firestore**
```
FIREBASE_PROJECT_ID=<your-project-id>
FIREBASE_PRIVATE_KEY=<your-private-key>
FIREBASE_CLIENT_EMAIL=<your-client-email>
```

**Option C: MongoDB**
```
DATABASE_URL=mongodb+srv://user:password@cluster.mongodb.net/riskshield
```

**Option D: SQLite (default, no configuration needed)**
- Will use `instance/riskshield.db` in the application

**Other Variables:**
```
FLASK_ENV=production
PYTHONUNBUFFERED=1
SECRET_KEY=<generate-a-strong-random-key>
JWT_SECRET=<generate-another-random-key>
```

### 4. Deploy
1. Click "Create Web Service"
2. Render will automatically:
   - Install system dependencies (portaudio19-dev)
   - Install Python packages from requirements.txt
   - Start the Gunicorn server
   - Enable auto-deploy for future git pushes

### 5. Monitor Deployment
- Watch the **Logs** tab during deployment
- Should see: `Building wheel for PyAudio...` → `successfully built PyAudio`
- Final log: `Listening on 0.0.0.0:10000` (or similar port)

## Troubleshooting

### PyAudio Build Failures
**Error:** `fatal error: portaudio.h: No such file or directory`

**Solution:** render.yaml automatically installs `portaudio19-dev`. If still failing:
1. Check Logs tab for system package installation output
2. Verify render.yaml is configured correctly
3. Try manual rebuild: In Render dashboard, click "Manual Deploy" → select latest commit

### Database Connection Issues
**Error:** `could not connect to database`

**Solution:** 
1. Verify DATABASE_URL environment variable is set correctly
2. For PostgreSQL: ensure IP allowlist includes Render IPs
3. For MongoDB: ensure connection string allows Render IPs (IP Allowlist)
4. For Firestore: verify credentials are valid JSON (check for line breaks)

### Audio Processing Not Working
**Error:** `RuntimeError: Failed to detect any device`

**Solution:** 
- Render web services don't have audio devices (headless environment)
- Audio detection works for uploaded files, not microphone input
- This is expected; use file upload instead of live recording

### Memory Limit
**Error:** `Container exceeded memory limit`

**Solution:**
- ML models use significant RAM
- Upgrade to paid Render plan for more memory (Starter: 512MB → Standard: 2GB)
- Or optimize model loading (load models only when needed)

### Timeout Issues
**Error:** `application failed to respond within timeout`

**Solution:**
- Large file uploads/processing may exceed 30-second default
- render.yaml sets Gunicorn timeout to 120 seconds
- For longer operations, implement background job processing with Render Jobs

## Performance Notes

### Expected Response Times
- **Image Analysis:** 2-5 seconds (depends on size)
- **Video Analysis:** 30-60+ seconds (depends on duration and frame count)
- **Audio Analysis:** 10-30 seconds (depends on duration)
- **URL Scanning:** <1 second
- **QR Code Detection:** 1-3 seconds
- **Chat Response:** 2-5 seconds (Groq API dependent)

### Cold Starts
First request after deployment may take 10-30 seconds as:
1. Flask app initializes
2. ML models load into memory
3. Database connections establish

Subsequent requests will be fast (cache-warm).

## Monitoring & Debugging

### View Logs
```bash
# In Render dashboard: Services → riskshield → Logs tab
# Or use Render CLI if installed:
render logs --service=riskshield
```

### Health Check
Test deployment at: `https://<your-service>.onrender.com/health`
Expected response: `{"status": "ok"}`

### Test Endpoints
```bash
# Test API is running
curl https://<your-service>.onrender.com/health

# Test URL scanner
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  https://<your-service>.onrender.com/api/scanner/url

# Test QR scanner
curl -X POST \
  -F "image=@qr_code.jpg" \
  https://<your-service>.onrender.com/api/scanner/qr
```

## Maintenance

### Auto-Deploy
- Enabled in render.yaml
- Any git push to main branch triggers automatic deployment
- Check Logs tab to monitor deployments

### Updating Dependencies
1. Update requirements.txt locally
2. Commit and push to GitHub
3. Render automatically redeploys with new dependencies

### Redeploying
In Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select branch and click deploy

## Cost Considerations

**Free Tier Limitations:**
- One free instance available
- Service spins down after 15 minutes of inactivity
- Limited to smaller ML model inference

**Recommended for Production:**
- Starter Plan ($7/month): 512MB RAM, always on
- Standard Plan ($25/month): 2GB RAM, faster cold starts
- For ML: Keep ML models cached, consider pre-warming on startup

## Next Steps

1. ✅ render.yaml already configured
2. ✅ build.sh already in place
3. ⏭️ Push code to GitHub
4. ⏭️ Create Render web service
5. ⏭️ Configure environment variables
6. ⏭️ Monitor first deployment
7. ⏭️ Test all endpoints

## Support

For Render-specific issues:
- [Render Docs](https://render.com/docs)
- [Render Support](https://render.com/docs/support)

For RiskShield-specific issues:
- Check [QUICK_START.md](QUICK_START.md)
- Check [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
