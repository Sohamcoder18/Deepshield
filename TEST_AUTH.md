# Authentication System Testing Guide

## Quick Start

### 1. Install Requirements
```bash
cd d:\hackethon\backend
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
python app.py
```
Server will run at: `http://localhost:5000`

### 3. Access Frontend
Open in browser:
- Main Site: `http://localhost:8000` or open `index.html` in browser
- Login: `http://localhost:8000/login.html`
- Sign Up: `http://localhost:8000/signup.html`

## Test Scenarios

### Scenario 1: New User Sign Up
**Steps:**
1. Open `signup.html`
2. Enter name: "Test User"
3. Enter email: "test@example.com"
4. Click "Send Verification OTP"
5. Check email inbox for OTP
6. Enter 6-digit OTP
7. Click "Verify & Create Account"

**Expected Result:**
- User account created in MongoDB
- JWT token stored in localStorage
- Redirect to home page
- Email displayed in navbar

---

### Scenario 2: Existing User Login
**Steps:**
1. Open `login.html`
2. Enter email: "test@example.com" (from previous signup)
3. Click "Send OTP"
4. Check email for OTP
5. Enter 6-digit OTP
6. Click "Verify & Sign In"

**Expected Result:**
- User logged in successfully
- JWT token stored in localStorage
- Redirect to home page
- User email shown in navbar

---

### Scenario 3: Image Analysis with Notification
**Steps:**
1. Ensure you're logged in
2. Go to "Image Detection"
3. Upload an image file
4. Click "Analyze Image"
5. Wait for analysis to complete
6. Check email for analysis results

**Expected Result:**
- Analysis completes successfully
- Email received with results summary
- Result shows in DeepShield format

---

### Scenario 4: Video Analysis with Notification
**Steps:**
1. Ensure you're logged in
2. Go to "Video Detection"
3. Upload a video file
4. Select frame count (15-30)
5. Click "Analyze Video"
6. Check email for results

**Expected Result:**
- Video analysis completes
- Email includes frame analysis summary
- Notification displays completion message

---

### Scenario 5: Audio Analysis with Notification
**Steps:**
1. Ensure you're logged in
2. Go to "Audio Detection"
3. Upload an audio file
4. Click "Analyze Audio"
5. Wait for analysis
6. Check email for notification

**Expected Result:**
- Audio analysis completes
- Email sent with speech synthesis detection results
- Notification displays

---

### Scenario 6: OTP Timeout and Resend
**Steps:**
1. Click "Send OTP"
2. Wait for timer (120 seconds)
3. After timer expires, click "Resend OTP"
4. New OTP sent to email

**Expected Result:**
- Timer displays countdown
- Resend button disabled until timeout
- Resend button enabled after 120s
- New OTP can be used

---

### Scenario 7: Invalid OTP
**Steps:**
1. Request OTP
2. Enter wrong 6-digit code
3. Click verify

**Expected Result:**
- Error message: "Invalid OTP"
- Counter increases for failed attempts
- After 3 failed attempts: "Too many attempts. Request a new OTP."

---

### Scenario 8: Logout
**Steps:**
1. Click user email in navbar
2. Click "Logout" button

**Expected Result:**
- Token removed from localStorage
- User email removed from localStorage
- Redirect to home page
- Sign In link appears in navbar

---

## API Testing with CURL

### Test 1: Send OTP for Signup
```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "isSignup": true
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "OTP sent to testuser@example.com",
  "email": "testuser@example.com"
}
```

---

### Test 2: Signup with OTP
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "fullName": "Test User",
    "otp": "REPLACE_WITH_ACTUAL_OTP"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Account created successfully",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "email": "testuser@example.com"
}
```

---

### Test 3: Send OTP for Login
```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "isSignup": false
  }'
```

---

### Test 4: Login with OTP
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "otp": "REPLACE_WITH_ACTUAL_OTP"
  }'
```

---

### Test 5: Get User Profile (Protected)
```bash
curl -X GET http://localhost:5000/api/auth/user \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response:**
```json
{
  "email": "testuser@example.com",
  "full_name": "Test User",
  "created_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T15:45:00",
  "total_analyses": 0
}
```

---

### Test 6: Image Analysis with Email
```bash
curl -X POST http://localhost:5000/api/analyze/image \
  -F "file=@path/to/image.jpg" \
  -F "userEmail=testuser@example.com"
```

---

### Test 7: Logout (Protected)
```bash
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

---

## Common Issues & Solutions

### Issue: OTP Not Received
**Solution:**
1. Check email spam/junk folder
2. Verify Brevo API key in app.py
3. Check internet connection
4. Try with different email address

### Issue: "Email already registered"
**Solution:**
- Email already has account
- Use different email or login instead

### Issue: "Email not found"
**Solution:**
- Email not registered in system
- Go to signup page instead

### Issue: JWT Token Error
**Solution:**
1. Ensure PyJWT is installed: `pip install PyJWT==2.8.0`
2. Token format: `Bearer token_here` (with space)
3. Check token hasn't expired

### Issue: CORS Error
**Solution:**
- Backend already has CORS enabled
- Check API URL is correct
- Backend must be running on port 5000

### Issue: Analysis Not Sending Email
**Solution:**
1. Verify user email is provided in form
2. Check backend logs for errors
3. Verify Brevo API key is valid
4. Check email spam folder

---

## Performance Testing

### Load Test: Multiple OTP Requests
```bash
for i in {1..10}; do
  curl -X POST http://localhost:5000/api/auth/send-otp \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"test$i@example.com\",\"isSignup\":true}" &
done
```

---

## Data Verification

### Check MongoDB Users
```javascript
// In MongoDB Shell
use deepfakedatabase
db.users.find().pretty()
```

### Check Analysis Results
```javascript
db.analysis_results.find().pretty()
```

### Check OTP Cache (In Backend)
Add logging in app.py to print OTP_CACHE:
```python
print("Current OTP Cache:", OTP_CACHE)
```

---

## Email Verification

### Check Email Format
The email should come from:
- **From:** noreply@deepshield.com
- **Subject:** "Your Verification Code" or "DeepShield - Your Analysis Results"

### Check Email Content
- OTP emails have 6-digit code in large font
- Analysis emails have results summary
- All emails include footer with copyright

---

## Browser Console Testing

### Check localStorage
```javascript
// In browser console
localStorage.getItem('authToken')
localStorage.getItem('userEmail')
```

### Clear localStorage
```javascript
localStorage.clear()
```

### Check Network Requests
1. Open DevTools (F12)
2. Go to Network tab
3. Perform login/signup
4. Check requests to `/api/auth/send-otp`, `/api/auth/signup`, etc.
5. Verify response status is 200

---

## Success Checklist

- [ ] User can sign up with email and OTP
- [ ] User receives OTP in email
- [ ] User can login with OTP
- [ ] JWT token stored in localStorage
- [ ] User email displayed in navbar
- [ ] User can perform image analysis
- [ ] User receives analysis result email
- [ ] User can logout successfully
- [ ] OTP timer counts down correctly
- [ ] Resend button works after timeout
- [ ] Invalid OTP shows error message
- [ ] Protected endpoints reject invalid tokens
- [ ] Email notifications have correct format

