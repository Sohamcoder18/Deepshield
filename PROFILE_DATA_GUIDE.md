# Profile Data Fetching Guide

## Overview
The profile page now fetches user data from MongoDB via the backend API and displays it. Users can also edit and save their profile information.

## Features Implemented

### 1. **User Profile Fetching** ✅
- **Endpoint**: `GET /api/auth/user`
- **Authentication**: Requires JWT token in Authorization header
- **Data Returned**:
  - `email` - User's email address
  - `full_name` - Full name
  - `phone_number` - Phone number
  - `date_of_birth` - Date of birth
  - `country` - Country
  - `occupation` - Occupation
  - `created_at` - Account creation date
  - `last_login` - Last login date
  - `total_analyses` - Total analysis count

### 2. **User Profile Update** ✅
- **Endpoint**: `POST /api/auth/update-profile`
- **Authentication**: Requires JWT token
- **Data Updated**: Any of the fields above can be updated
- **Response**: Success message with status code 200

### 3. **Edit Profile Feature** ✅
- Click "✏️ Edit Profile" button to enable edit mode
- All profile fields become editable input fields
- Button changes to "💾 Save Profile"
- Changes are saved to MongoDB
- Profile automatically reloads after save

## How Data Flows

### Sign Up → MongoDB → Profile Display
```
User fills signup form
    ↓
Submits signup with: email, fullName, phoneNumber, dateOfBirth, country, occupation
    ↓
Backend creates user in MongoDB with all data
    ↓
User logs in with OTP
    ↓
JWT token is generated and stored
    ↓
User navigates to Profile page
    ↓
Profile page fetches data from `/api/auth/user`
    ↓
MongoDB returns user data
    ↓
Data is displayed in profile page
```

## Testing the Profile Feature

### Test 1: Sign Up with Complete Profile Data
1. Go to signup page
2. Fill all fields:
   - Email: your@email.com
   - Full Name: John Doe
   - Phone Number: +1234567890
   - Date of Birth: 1990-01-15
   - Country: USA
   - Occupation: Developer
3. Enter OTP when received (check console)
4. Click Sign Up
5. Go to Profile page
6. **Expected**: All data should display correctly

### Test 2: Update Profile
1. On Profile page, click "✏️ Edit Profile"
2. Update fields:
   - Change Full Name
   - Update Phone Number
   - Change Country
3. Click "💾 Save Profile"
4. **Expected**: 
   - Success message appears
   - Page reloads with new data
   - Changes are visible in MongoDB

### Test 3: Fallback When Backend is Unavailable
1. Stop the Flask backend
2. Go to Profile page
3. **Expected**:
   - Error message appears
   - Fallback data is shown (from localStorage)
   - Email from localStorage is displayed
   - Other fields show "-" (not set)

### Test 4: Missing Profile Data
1. Sign up with minimal data (just email and name)
2. Go to Profile page
3. **Expected**:
   - Fields without data show "-"
   - Other fields display correctly
   - No errors in console

## Troubleshooting

### Problem: Profile page shows "-" for all fields
**Solution**:
1. Check if backend is running: `python backend/app.py`
2. Check browser console (F12) for error messages
3. Verify JWT token is valid: `console.log(localStorage.getItem('authToken'))`
4. Check MongoDB connection in backend logs

### Problem: Edit mode doesn't work
**Solution**:
1. Check browser console for JavaScript errors
2. Ensure backend endpoint `/api/auth/update-profile` is accessible
3. Verify user is authenticated (token should exist)

### Problem: Profile page shows only email
**Solution**:
1. MongoDB might not be connected - check backend logs
2. Sign up again with complete profile data
3. Ensure all fields are being sent during signup

## MongoDB Schema

The user profile data is stored in the `users` collection:

```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-15T00:00:00",
  "country": "USA",
  "occupation": "Developer",
  "created_at": "2026-02-01T12:30:45.123456",
  "last_login": "2026-02-01T12:35:20.654321",
  "total_analyses": 5,
  "updated_at": "2026-02-01T14:00:00.123456"
}
```

## API Endpoints Reference

### Get User Profile
```bash
curl -X GET http://localhost:5000/api/auth/user \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Response (200 OK)**:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "date_of_birth": "1990-01-15",
  "country": "USA",
  "occupation": "Developer",
  "created_at": "2026-02-01T12:30:45",
  "last_login": "2026-02-01T12:35:20",
  "total_analyses": 5
}
```

### Update User Profile
```bash
curl -X POST http://localhost:5000/api/auth/update-profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Doe",
    "phone_number": "+9876543210",
    "occupation": "Designer"
  }'
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Profile updated successfully"
}
```

## Features Added in This Update

1. **Better Error Handling**
   - Console logging for debugging
   - User-friendly error messages
   - Fallback display using localStorage

2. **Enhanced Edit Mode**
   - Inline editing with proper styling
   - Cyan glow effects on input focus
   - Save validation
   - Success/error notifications

3. **Backend Integration**
   - New endpoint: `/api/auth/update-profile`
   - Proper MongoDB update operations
   - Timestamp tracking for updates
   - Data validation

4. **User Experience**
   - Loading state while fetching data
   - Smooth transitions
   - Clear visual feedback
   - Responsive design

## Next Steps

To fully test the profile feature:

1. **Start Backend**:
   ```bash
   cd backend
   python app.py
   ```

2. **Verify MongoDB Connection**:
   - Check if "✓ Connected to MongoDB successfully" appears in console
   - If not, verify `.env` file has correct `MONGODB_URI`

3. **Test Sign Up → Profile Flow**:
   - Go to signup.html
   - Fill all fields with complete data
   - Sign up and verify
   - Go to profile.html
   - Verify all data displays

4. **Test Edit Profile**:
   - Click "✏️ Edit Profile"
   - Change some fields
   - Click "💾 Save Profile"
   - Verify changes are saved

5. **Monitor Console**:
   - Open browser DevTools (F12)
   - Check Console tab for any errors
   - Check Network tab to see API requests/responses

## Important Notes

- Profile data is only visible to logged-in users
- Tokens expire after the session
- All profile updates are timestamped in MongoDB
- Email cannot be changed after signup (optional: can add verification flow)
- All date fields should be in ISO format (YYYY-MM-DD)
