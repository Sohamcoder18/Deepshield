# Quick Fix: Profile Data Not Showing - Action Items

## What's the Issue?
The profile page is not displaying user data because:
1. Backend might not be running
2. MongoDB might not be connected  
3. API endpoints need to be working

## Quick Fix - Follow These Steps

### Step 1: Verify Backend is Running
```bash
cd d:\hackethon\backend
python app.py
```

**Expected output**:
```
✓ Connected to MongoDB successfully
 * Running on http://0.0.0.0:5000
```

### Step 2: Verify MongoDB Connection
Look for this message in the backend console:
- ✅ `✓ Connected to MongoDB successfully` - MongoDB is working
- ❌ `✗ Could not connect to MongoDB` - Check .env file

### Step 3: Sign Up with Complete Profile Data
1. Open `http://localhost:5000/../signup.html` (or use the frontend)
2. Fill **ALL** fields:
   ```
   Email: test@example.com
   Full Name: Your Name
   Phone: +1234567890
   Date of Birth: 1990-01-01
   Country: USA
   Occupation: Developer
   ```
3. Enter OTP (check backend console for OTP)
4. Click "Sign Up"

### Step 4: Go to Profile Page
1. After signup, you'll be logged in
2. Click "👤 Profile" in navbar or go to `/profile.html`
3. **Expected**: All your data should display!

### Step 5: Test Edit Profile (Optional)
1. Click "✏️ Edit Profile" button
2. Update any field
3. Click "💾 Save Profile"
4. Verify data is updated

## What Each Field Should Show

| Field | What It Shows | Where From |
|-------|---------------|-----------|
| Full Name | Name entered during signup | MongoDB `full_name` |
| Email | Email used for signup | MongoDB `email` |
| Phone Number | Phone number entered | MongoDB `phone_number` or `-` |
| Date of Birth | DOB entered during signup | MongoDB `date_of_birth` or `-` |
| Country | Country entered | MongoDB `country` or `-` |
| Occupation | Occupation entered | MongoDB `occupation` or `-` |
| Total Analyses | Number of detections | MongoDB `total_analyses` (starts at 0) |
| Member Since | Account creation date | MongoDB `created_at` |
| Last Active | Last login date | MongoDB `last_login` |

## Debugging: Open Browser Console

1. Press `F12` to open Developer Tools
2. Go to **Console** tab
3. You'll see logs like:
   ```
   Loading profile with token: eyJhbGc...
   Response status: 200
   User data received: {email: "test@example.com", full_name: "Your Name", ...}
   ```

If you see errors, check:
- `Response status: 401` → Token is invalid, login again
- `Response status: 404` → User not found in database
- `Response status: 503` → MongoDB not connected, check backend

## Check MongoDB Directly (Advanced)

Connect to MongoDB compass or MongoDB Atlas:
- Database: `deepfakedatabase`
- Collection: `users`
- Look for your email document
- Should have all fields: `full_name`, `phone_number`, etc.

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Profile shows only email | Sign up with complete data, all fields required |
| Profile shows all dashes `-` | MongoDB not storing data, check backend connection |
| Edit button doesn't work | Ensure backend is running and reachable |
| "Failed to load profile" error | Check browser console, restart backend |
| Logged out immediately | Token might be invalid, sign up again |

## Files Modified

These files were updated to fix the issue:
- ✅ `/deepfake-detection/profile.html` - Enhanced error handling and edit mode
- ✅ `/backend/app.py` - Added `update-profile` endpoint
- ✅ New `/PROFILE_DATA_GUIDE.md` - Detailed documentation

## Endpoints Available

- `GET /api/auth/user` - Fetch user profile (requires token)
- `POST /api/auth/update-profile` - Update profile fields (requires token)
- `POST /api/auth/send-otp` - Get OTP for signup/login
- `POST /api/auth/signup` - Create new account with profile data
- `POST /api/auth/login` - Login with OTP

## Test Checklist

- [ ] Backend is running (`python app.py`)
- [ ] MongoDB connection shows `✓ Connected`
- [ ] Signed up with complete profile data
- [ ] Logged in successfully
- [ ] Profile page loads without errors
- [ ] Profile data displays correctly
- [ ] Edit profile works
- [ ] Changes save successfully

## Next Steps

Once profile is working:
1. Run detection features (image/video/audio)
2. Check if `total_analyses` count increases
3. Verify `last_login` updates after refresh
4. Test on mobile/tablet for responsive design

## Support

If profile still doesn't work:
1. Check backend console for error messages
2. Check browser console (F12) for errors
3. Verify `.env` file in backend has correct `MONGODB_URI`
4. Restart backend after any changes
5. Clear browser cache (Ctrl+Shift+Delete) and refresh

---

**Summary**: The profile feature is now complete! Just ensure the backend is running and you sign up with all profile fields. The data will automatically fetch and display on the profile page.
