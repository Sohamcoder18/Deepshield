# DeepShield Authentication & Notification System Setup

## Overview
This document outlines the new modern authentication system with email OTP verification and post-analysis email notifications.

## Features Implemented

### 1. **Email-Based OTP Authentication**
- Users can sign up or login using email and OTP (One-Time Password)
- 6-digit OTP sent via Brevo email service
- 120-second OTP expiry with resend functionality
- JWT token-based session management

### 2. **User Account Management**
- Modern sign-up form with email verification
- User profiles stored in MongoDB
- Track user analysis history
- Last login timestamp tracking

### 3. **Post-Analysis Email Notifications**
- Automatic email sent after each analysis (image/video/audio)
- Summary of results included in email
- Professional HTML formatted emails
- Only sent to authenticated users

### 4. **Frontend Updates**
- Modern login page (`login.html`)
- Professional signup page (`signup.html`)
- Authentication UI in navbar
- Sign in/Logout buttons
- User email display in navigation

## Authentication Flow

### Sign Up Flow
```
User → Email Input → Send OTP → Verify OTP → Create Account → JWT Token → Redirect to Home
```

### Login Flow
```
User → Email Input → Send OTP → Verify OTP → Verify User Exists → JWT Token → Redirect to Home
```

### Analysis with Notifications
```
Upload File → (Optional: User Email from localStorage) → Perform Analysis → Save Results → Send Email Notification
```

## Backend Endpoints

### Authentication Endpoints

#### `POST /api/auth/send-otp`
Sends OTP to user email
- **Parameters:**
  - `email` (string): User email address
  - `isSignup` (boolean): True for signup, False for login
- **Response:**
  ```json
  {
    "success": true,
    "message": "OTP sent to email@example.com",
    "email": "email@example.com"
  }
  ```

#### `POST /api/auth/verify-otp`
Verifies OTP for login
- **Parameters:**
  - `email` (string): User email
  - `otp` (string): 6-digit OTP
- **Response:**
  ```json
  {
    "success": true,
    "message": "OTP verified",
    "token": "jwt.token.here",
    "email": "email@example.com"
  }
  ```

#### `POST /api/auth/signup`
Creates new user account after OTP verification
- **Parameters:**
  - `email` (string): User email
  - `fullName` (string): User's full name
  - `otp` (string): 6-digit OTP
- **Response:**
  ```json
  {
    "success": true,
    "message": "Account created successfully",
    "token": "jwt.token.here",
    "email": "email@example.com"
  }
  ```

#### `POST /api/auth/login`
Logs in user after OTP verification
- **Parameters:**
  - `email` (string): User email
  - `otp` (string): 6-digit OTP
- **Response:**
  ```json
  {
    "success": true,
    "message": "Login successful",
    "token": "jwt.token.here",
    "email": "email@example.com"
  }
  ```

#### `GET /api/auth/user`
Gets authenticated user profile (requires token)
- **Headers:** `Authorization: Bearer jwt.token.here`
- **Response:**
  ```json
  {
    "email": "email@example.com",
    "full_name": "User Name",
    "created_at": "2024-01-15T10:30:00",
    "last_login": "2024-01-15T15:45:00",
    "total_analyses": 5
  }
  ```

#### `POST /api/auth/logout`
Logs out user (token-based, handled on frontend)
- **Headers:** `Authorization: Bearer jwt.token.here`
- **Response:**
  ```json
  {
    "success": true,
    "message": "Logged out successfully"
  }
  ```

## Frontend Pages

### `login.html`
- Modern authentication UI
- Email input field
- 6-digit OTP input with auto-focus
- 120-second timer with resend functionality
- Error and success messaging
- Responsive design

### `signup.html`
- Sign up form with email, name, and password fields
- OTP verification section
- Terms and conditions acceptance
- Responsive design matching login page

## Environment Configuration

### Required Environment Variables
Add to `.env` file:
```
GROQ_API_KEY=your_groq_api_key
JWT_SECRET=your_jwt_secret_key_here
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/
```

### Brevo API Configuration
The Brevo API key is configured directly in `app.py`:
```python
BREVO_API_KEY = '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'
```

## Email Templates

### OTP Email
```
Subject: Your Verification Code
- Professional branding with DeepShield logo
- 6-digit OTP prominently displayed
- Expiry time: 120 seconds
- Action: Sign Up or Log In
```

### Analysis Result Email
```
Subject: DeepShield - Your Analysis Results
- Analysis type (image/video/audio)
- Result status (Authentic/Likely Fake)
- Confidence percentage
- Trust score
- Recommendation
```

## Frontend Integration

### Storing User Data
```javascript
// After successful login/signup
localStorage.setItem('authToken', data.token);
localStorage.setItem('userEmail', data.email);
```

### Using Token for API Calls
```javascript
// For protected endpoints
const token = localStorage.getItem('authToken');
const headers = {
    'Authorization': `Bearer ${token}`
};
```

### Sending User Email with Analysis
```javascript
const formData = new FormData();
formData.append('file', file);

const userEmail = localStorage.getItem('userEmail');
if (userEmail) {
    formData.append('userEmail', userEmail);
}

fetch('/api/analyze/image', {
    method: 'POST',
    body: formData
});
```

## User Database Schema

### MongoDB Users Collection
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "full_name": "User Name",
  "created_at": "2024-01-15T10:30:00",
  "last_login": "2024-01-15T15:45:00",
  "total_analyses": 5
}
```

### Analysis Results (Updated)
Each analysis now includes user information:
```json
{
  "analysis_id": "uuid",
  "analysis_type": "image|video|audio",
  "file_name": "filename.ext",
  "user_email": "user@example.com",
  "results": {...},
  "timestamp": "2024-01-15T10:30:00"
}
```

## OTP Management

### OTP Cache (In-Memory)
```python
OTP_CACHE = {
    "email@example.com": {
        "otp": "123456",
        "expires": timestamp,
        "attempts": 0,
        "is_signup": True/False
    }
}
```

### OTP Rules
- **Length:** 6 digits
- **Expiry:** 120 seconds
- **Max Attempts:** 3 attempts before expiry
- **Resend:** Available after timer expires

## Security Considerations

1. **JWT Secret:** Change `JWT_SECRET` in production to a strong, random value
2. **HTTPS:** Use HTTPS in production to secure token transmission
3. **Token Expiry:** Consider adding token expiry time (currently no expiry)
4. **OTP Storage:** Currently uses in-memory cache (not persistent across restarts)
5. **Brevo API Key:** Keep secure, never commit to version control
6. **CORS:** Ensure CORS is properly configured for production domains

## Testing the System

### 1. Test OTP Generation and Email Sending
```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","isSignup":true}'
```

### 2. Test Sign Up
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","fullName":"Test User","otp":"123456"}'
```

### 3. Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","otp":"123456"}'
```

### 4. Test Protected Endpoint
```bash
curl -X GET http://localhost:5000/api/auth/user \
  -H "Authorization: Bearer your.jwt.token.here"
```

## Files Modified/Created

### New Files
- `login.html` - Login page with OTP
- `signup.html` - Sign up page with OTP
- `AUTHENTICATION_SETUP.md` - This documentation

### Modified Files
- `app.py` - Added authentication endpoints, email functions, notification system
- `requirements.txt` - Added PyJWT, requests packages
- `script.js` - Updated analysis functions to send real API calls and user email
- `styles.css` - Added animation styles for notifications

### Updated Endpoints
- `/api/analyze/image` - Now sends email notification to user
- `/api/analyze/video` - Now sends email notification to user
- `/api/analyze/audio` - Now sends email notification to user

## Future Enhancements

1. **Persistent OTP Storage:** Store OTPs in MongoDB instead of memory
2. **Token Refresh:** Implement refresh tokens for longer sessions
3. **Email Verification on Signup:** Verify email before account activation
4. **Password-less Login:** Consider password-less authentication entirely
5. **Rate Limiting:** Add rate limiting to prevent brute force attacks
6. **Analytics:** Track user analysis history and statistics
7. **User Preferences:** Allow users to customize notification settings
8. **Multi-factor Authentication:** Add optional 2FA with authenticator apps

## Troubleshooting

### OTP Not Received
- Check email spam folder
- Verify Brevo API key is correct
- Check internet connectivity
- Verify email address format

### JWT Token Errors
- Ensure PyJWT is installed: `pip install PyJWT==2.8.0`
- Verify JWT_SECRET is configured
- Check token format in Authorization header

### Analysis Notifications Not Sent
- Verify user email is provided in form data
- Check Brevo API key configuration
- Check backend logs for email sending errors
- Verify user is authenticated (token valid)

## Support

For issues or questions:
1. Check the backend logs in console
2. Check browser console for frontend errors (F12)
3. Verify API endpoint URLs are correct
4. Test API endpoints using curl or Postman

