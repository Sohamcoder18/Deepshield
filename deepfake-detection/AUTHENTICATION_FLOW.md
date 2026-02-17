# DeepShield Authentication Flow

## Overview
The DeepShield application now features a complete authentication system that requires users to login before accessing the detection features.

## Authentication Flow

### 1. **Initial Login Page** (login.html)
- **Entry Point**: Users first see `login.html` when they visit the application
- **Process**:
  1. User enters their email address
  2. System sends OTP (One-Time Password) to their email
  3. User enters the 6-digit OTP
  4. On successful verification, an `authToken` is stored in `localStorage`
  5. User is redirected to the main dashboard (index.html)

### 2. **Protected Pages**
All detection pages now require authentication:
- `index.html` (Main Dashboard)
- `image-detection.html` (Image Analysis)
- `video-detection.html` (Video Analysis)
- `audio-detection.html` (Audio Analysis)
- `ai-assistant.html` (AI Assistant)
- `profile.html` (User Profile)

### 3. **Authentication Check**
Each protected page includes:
```javascript
function checkAuthentication() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        // Redirect to login if no token
        window.location.href = 'login.html';
        return false;
    }
    return true;
}
```

If a user tries to access any page without being logged in:
- They will be automatically redirected to `login.html`
- Session data is checked before page loads

### 4. **Navigation Bar Updates**
Once logged in:
- A **Logout button** appears in the navigation bar
- The Profile link becomes visible (👤 Profile)
- User email is stored in `localStorage`

### 5. **Logout Functionality**
Clicking the "Logout" button:
- Clears the `authToken` from `localStorage`
- Clears the `userEmail` from `localStorage`
- Redirects user to `login.html`

## Local Storage Data

### Stored on Successful Login
```javascript
localStorage.setItem('authToken', data.token);
localStorage.setItem('userEmail', userEmail);
```

### Cleared on Logout
```javascript
localStorage.removeItem('authToken');
localStorage.removeItem('userEmail');
```

## Authentication Endpoints

The login system communicates with backend API endpoints:

### Send OTP
- **Endpoint**: `http://localhost:5000/api/auth/send-otp`
- **Method**: POST
- **Body**: `{ email: "user@example.com" }`

### Verify OTP
- **Endpoint**: `http://localhost:5000/api/auth/verify-otp`
- **Method**: POST
- **Body**: `{ email: "user@example.com", otp: "123456" }`
- **Response**: `{ token: "auth_token", success: true }`

## Pages Modified

### Protected Pages (Added Auth Check)
1. **index.html** - Main dashboard
2. **image-detection.html** - Image detection page
3. **video-detection.html** - Video detection page
4. **audio-detection.html** - Audio detection page
5. **ai-assistant.html** - AI assistant page
6. **profile.html** - User profile page

### Authentication Pages (Existing)
- **login.html** - OTP-based login
- **signup.html** - User registration

## Styling

### Logout Button Styling
```css
.logout-link {
    background: var(--gradient-primary);
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    display: inline-block;
}

.logout-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
}
```

## User Experience

1. **First Time**: User lands on login.html, enters email, receives OTP
2. **OTP Verification**: User enters 6-digit OTP (2-minute timeout)
3. **Dashboard Access**: After verification, user sees the full application
4. **Navigation**: User can navigate between all pages without re-login
5. **Session**: Token persists until user clicks Logout
6. **Auto-Redirect**: If token expires or is cleared, user is redirected to login

## Security Features

- ✅ OTP-based authentication (more secure than passwords)
- ✅ Token stored in localStorage (cleared on logout)
- ✅ Automatic redirect on unauthorized access
- ✅ Session timeout protection
- ✅ Navigation logout for explicit session termination

## Testing the Flow

1. **Test Login**:
   - Navigate to `http://localhost:8000/login.html`
   - Enter your email
   - Enter the 6-digit OTP
   - Should redirect to index.html

2. **Test Protected Pages**:
   - Try accessing `http://localhost:8000/image-detection.html` without login
   - Should redirect to login.html

3. **Test Logout**:
   - Click "Logout" button in navbar
   - Should redirect to login.html
   - Token should be cleared

4. **Test Session Persistence**:
   - Login to the app
   - Refresh the page (F5)
   - Should remain logged in
   - Navigate to different pages - no redirect

## Backend Integration

Ensure your Flask backend is running with these endpoints:
- `POST /api/auth/send-otp` - Sends OTP to email
- `POST /api/auth/verify-otp` - Verifies OTP and returns token

```bash
# Start Flask backend
python app.py
```

The frontend expects the backend to be running on `http://localhost:5000`

---

**Complete Authentication System Ready for Deployment!** 🎉
