# Authentication System - Quick Start Guide

## How to Test the Login Flow

### Step 1: Start the Frontend Server
```bash
cd d:\hackethon\deepfake-detection
python -m http.server 8000
```

### Step 2: Start the Backend Server
```bash
cd d:\hackethon\backend
python app.py
```

### Step 3: Test the Authentication Flow

#### **Test 1: First Time Access**
1. Open browser: `http://localhost:8000/index.html`
2. **Expected**: Redirected to `login.html` automatically
3. **Reason**: No authentication token found in localStorage

#### **Test 2: Login with OTP**
1. At login page, enter your email: `user@example.com`
2. Click "Send OTP" button
3. Backend sends OTP to your email
4. Enter the 6-digit OTP received
5. Click "Verify OTP"
6. **Expected**: Redirected to `index.html` with Logout button visible

#### **Test 3: Protected Pages Access**
After logging in:
1. ✅ Can access: `http://localhost:8000/index.html`
2. ✅ Can access: `http://localhost:8000/image-detection.html`
3. ✅ Can access: `http://localhost:8000/video-detection.html`
4. ✅ Can access: `http://localhost:8000/audio-detection.html`
5. ✅ Can access: `http://localhost:8000/ai-assistant.html`
6. ✅ Can access: `http://localhost:8000/profile.html`

#### **Test 4: Logout Functionality**
1. Click "Logout" button in navbar (top-right)
2. **Expected**: Redirected to login page
3. Authentication token cleared from localStorage
4. Trying to access any protected page will redirect to login

#### **Test 5: Access Without Login**
1. Open a new browser tab
2. Try direct access: `http://localhost:8000/image-detection.html`
3. **Expected**: Automatically redirected to login.html

#### **Test 6: Session Persistence**
1. Login to the app
2. Press F5 (refresh the page)
3. **Expected**: Remain logged in, no redirect to login
4. Navigate between pages without re-authentication

#### **Test 7: Clear localStorage Manually**
1. Open DevTools (F12)
2. Go to Application → Local Storage
3. Remove `authToken` and `userEmail`
4. Refresh the page
5. **Expected**: Redirected to login.html

## Navigation Bar Changes

### Before Login
- Shows: Home, Image Detection, Video Detection, Audio Detection, AI Assistant, About
- Profile link: Hidden
- Logout button: None

### After Login
- Shows: All above links
- Profile link: Visible (👤 Profile)
- Logout button: Added at the end with gradient styling

## Logout Button Styling

The logout button has:
- **Background**: Gradient (blue to cyan)
- **Color**: White
- **Padding**: 8px 16px
- **Hover Effect**: Moves up 2px with shadow
- **Font Size**: 13px (smaller than nav links)
- **Shape**: Rounded corners

## LocalStorage Data

After successful login:
```javascript
localStorage.authToken = "jwt_token_from_backend"
localStorage.userEmail = "user@example.com"
```

After logout:
```javascript
// Both are removed/cleared
localStorage.authToken = undefined
localStorage.userEmail = undefined
```

## Endpoints Used

### Backend API Calls
1. **Send OTP**
   - URL: `http://localhost:5000/api/auth/send-otp`
   - Method: POST
   - Body: `{ email: "user@example.com" }`

2. **Verify OTP**
   - URL: `http://localhost:5000/api/auth/verify-otp`
   - Method: POST
   - Body: `{ email: "user@example.com", otp: "123456" }`
   - Response: `{ token: "jwt_token", email: "user@example.com" }`

## Debug Tips

### Check if Logged In
1. Open DevTools → Console
2. Type: `localStorage.getItem('authToken')`
3. Should return the token (not null)

### Manually Set Token (for testing)
1. Open DevTools → Console
2. Type:
```javascript
localStorage.setItem('authToken', 'test-token');
localStorage.setItem('userEmail', 'test@example.com');
```
3. Refresh page - should load without redirect

### Check Page Auth Status
1. Right-click → Inspect
2. Go to Console
3. Type: `checkAuthentication()`
4. Should return `true` if logged in

## Files Modified

### Authentication Check Added To:
- ✅ index.html
- ✅ image-detection.html
- ✅ video-detection.html
- ✅ audio-detection.html
- ✅ ai-assistant.html
- ✅ profile.html

### CSS Updated:
- ✅ styles.css (added `.logout-link` styling)

### Documentation Created:
- ✅ AUTHENTICATION_FLOW.md (detailed documentation)
- ✅ AUTHENTICATION_QUICK_START.md (this file)

## Common Issues & Fixes

### Issue: Stuck on Login Page
**Solution**: 
- Check if backend is running: `python app.py`
- Check backend logs for errors
- Verify email format is correct

### Issue: OTP Not Received
**Solution**:
- Check spam/junk folder
- Verify email in backend is configured correctly
- Check if Brevo email service is working

### Issue: Token Not Persisting After Refresh
**Solution**:
- Check if localStorage is enabled in browser
- Not a Private/Incognito window
- Check browser privacy settings

### Issue: Logout Not Working
**Solution**:
- Check browser console for JavaScript errors
- Clear cache and cookies
- Hard refresh (Ctrl+Shift+R)

## Success Indicators

✅ **System is working correctly when:**
1. New users see login page first
2. After login, main dashboard loads
3. Profile link appears in navbar
4. Logout button appears in navbar
5. Clicking logout clears data and shows login page
6. Refreshing page keeps user logged in
7. Accessing pages without login redirects to login

---

**Ready to test! Start servers and begin testing the authentication flow.** 🔐
