# DeepShield Authentication - Visual System Overview

## System Architecture Diagram

```
╔════════════════════════════════════════════════════════════════════════╗
║                    DEEPSHIELD APPLICATION FLOW                          ║
╚════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│  USER ACCESSES: http://localhost:8000/index.html                    │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  CHECK localStorage        │
        │  for authToken             │
        └────┬──────────────────┬────┘
             │                  │
             NO                 YES
             │                  │
             ▼                  ▼
      ┌──────────────┐   ┌─────────────────┐
      │ REDIRECT TO  │   │ PAGE LOADS      │
      │ login.html   │   │ ✓ Full access   │
      │              │   │ ✓ Logout button │
      │              │   │ ✓ Profile link  │
      └──────┬───────┘   └────────┬────────┘
             │                    │
             └────────┬───────────┘
                      │
            ┌─────────▼──────────┐
            │  USER LOGGED IN    │
            │  Can access:       │
            │  ✓ index.html      │
            │  ✓ img-detect      │
            │  ✓ vid-detect      │
            │  ✓ aud-detect      │
            │  ✓ ai-assistant    │
            │  ✓ profile         │
            └─────────┬──────────┘
                      │
             ┌────────▼────────┐
             │  USER CLICKS    │
             │  LOGOUT BUTTON  │
             └────────┬────────┘
                      │
             ┌────────▼──────────────┐
             │ CLEAR localStorage    │
             │ • Remove authToken    │
             │ • Remove userEmail    │
             └────────┬──────────────┘
                      │
             ┌────────▼───────────┐
             │ REDIRECT TO        │
             │ login.html         │
             └────────────────────┘
```

## Page Protection Architecture

```
╔════════════════════════════════════════════════════════════════════════╗
║                      PROTECTED PAGES STRUCTURE                          ║
╚════════════════════════════════════════════════════════════════════════╝

EVERY PROTECTED PAGE CONTAINS:

┌─────────────────────────────────────────────────────┐
│  <body>                                             │
│    <nav> Navbar with Links</nav>                    │
│    ... Page Content ...                             │
│                                                     │
│  <script>                                           │
│    // 1. Check Authentication                      │
│    function checkAuthentication() {                │
│      const token = localStorage.getItem('auth');   │
│      if (!token) {                                 │
│        window.location.href = 'login.html';        │
│        return false;                               │
│      }                                             │
│      return true;                                  │
│    }                                               │
│                                                     │
│    // 2. Setup Navigation                          │
│    function setupNavigation() {                    │
│      if (token) {                                  │
│        // Add Logout button to navbar              │
│        // Make profile link visible                │
│      }                                             │
│    }                                               │
│                                                     │
│    // 3. Execute on Page Load                      │
│    document.addEventListener(                     │
│      'DOMContentLoaded',                           │
│      function() {                                  │
│        checkAuthentication();                      │
│        setupNavigation();                          │
│      }                                             │
│    );                                              │
│  </script>                                         │
│</body>                                             │
└─────────────────────────────────────────────────────┘
```

## Navigation Bar States

### BEFORE Login
```
┌─────────────────────────────────────────────────────┐
│ 🛡️ DeepShield  Home │ Image │ Video │ Audio │ AI │  │
└─────────────────────────────────────────────────────┘
Profile Link: HIDDEN
Logout Button: NONE
```

### AFTER Login
```
┌───────────────────────────────────────────────────────────────────┐
│ 🛡️ DeepShield  Home │ Image │ Video │ Audio │ AI │ 👤 Profile │ │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │ Logout Button (Blue Gradient)                           │     │
│  │ Hover: Lifts up with shadow effect                      │     │
│  └─────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────┘
Profile Link: VISIBLE
Logout Button: VISIBLE
```

## Data Flow During Login

```
┌──────────────────────────────────────────────────────────────┐
│ USER ENTERS EMAIL: user@example.com                          │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │ POST /api/auth/send-otp        │
    │ {email: "user@example.com"}     │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │ Backend sends OTP via email     │
    │ (User checks spam folder)       │
    └────────────────┬────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ USER RECEIVES: 123456 (6-digit OTP)                          │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────┐
  │ USER ENTERS OTP IN FORM:         │
  │ ┌──┬──┬──┬──┬──┬──┐             │
  │ │1 │2 │3 │4 │5 │6 │ (Auto-focus) │
  │ └──┴──┴──┴──┴──┴──┘             │
  │                                  │
  │ Click: Verify OTP               │
  └──────────────┬───────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────────────┐
  │ POST /api/auth/verify-otp                   │
  │ {                                            │
  │   email: "user@example.com",                 │
  │   otp: "123456"                              │
  │ }                                            │
  └──────────────┬───────────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────────────┐
  │ Backend Response:                            │
  │ {                                            │
  │   success: true,                             │
  │   token: "eyJhbGciOiJIUzI1NiIs...",         │
  │   email: "user@example.com"                  │
  │ }                                            │
  └──────────────┬───────────────────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────────────────┐
  │ Frontend:                                    │
  │ • Store token in localStorage                │
  │ • Store email in localStorage                │
  │ • Redirect to index.html                     │
  │ • Show success message                       │
  └──────────────┬───────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│ ✅ USER LOGGED IN - Dashboard Loaded with Logout Button     │
└──────────────────────────────────────────────────────────────┘
```

## localStorage Management

```
┌─────────────────────────────────────────────────────┐
│          BROWSER - localStorage                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Status: NOT LOGGED IN                             │
│  ────────────────────────────────────────────────  │
│  authToken: [empty]                                │
│  userEmail: [empty]                                │
│                                                     │
│           ↓↓↓ User Logs In ↓↓↓                      │
│                                                     │
│  Status: LOGGED IN                                 │
│  ────────────────────────────────────────────────  │
│  authToken: "eyJhbGciOiJIUzI1NiIs..."             │
│  userEmail: "user@example.com"                     │
│                                                     │
│           ↓↓↓ User Clicks Logout ↓↓↓               │
│                                                     │
│  Status: LOGGED OUT                                │
│  ────────────────────────────────────────────────  │
│  authToken: [removed]                              │
│  userEmail: [removed]                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Files Protected & Unprotected

```
┌──────────────────────────────────────────────────────┐
│            PROTECTED PAGES (Auth Required)            │
├──────────────────────────────────────────────────────┤
│ 1. index.html ..................... 🔒 Protected     │
│ 2. image-detection.html ........... 🔒 Protected     │
│ 3. video-detection.html ........... 🔒 Protected     │
│ 4. audio-detection.html ........... 🔒 Protected     │
│ 5. ai-assistant.html ............. 🔒 Protected     │
│ 6. profile.html ................... 🔒 Protected     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│       UNPROTECTED PAGES (No Auth Required)           │
├──────────────────────────────────────────────────────┤
│ 1. login.html ..................... 🔓 Public        │
│ 2. signup.html .................... 🔓 Public        │
└──────────────────────────────────────────────────────┘
```

## Component States

```
┌─────────────────────────────────┐
│      Authentication State        │
├─────────────────────────────────┤
│                                 │
│ STATE 1: VISITOR                │
│ ├─ Not logged in                │
│ ├─ Sees: Login page             │
│ ├─ Can do: Enter email, Login   │
│ └─ Cannot: Access dashboard     │
│                                 │
│ STATE 2: LOGGED IN              │
│ ├─ Has auth token               │
│ ├─ Sees: Full application       │
│ ├─ Can do: Use all features     │
│ └─ Sees: Logout button          │
│                                 │
│ STATE 3: SESSION ENDED          │
│ ├─ Clicked logout               │
│ ├─ Token cleared                │
│ ├─ Sees: Login page             │
│ └─ Must: Login again            │
│                                 │
└─────────────────────────────────┘
```

## CSS Styling for Logout Button

```
┌────────────────────────────────────────────────────┐
│           LOGOUT BUTTON STYLING                    │
├────────────────────────────────────────────────────┤
│                                                    │
│ ┌─────────────────────────────────────────────┐  │
│ │             📊 LOGOUT 📊                     │  │
│ ├─────────────────────────────────────────────┤  │
│ │ Background: Gradient (Blue → Cyan)          │  │
│ │ Color: White                                │  │
│ │ Padding: 8px 16px                           │  │
│ │ Border Radius: 6px                          │  │
│ │ Font Size: 13px                             │  │
│ │ Display: Inline Block                       │  │
│ │                                              │  │
│ │ HOVER STATE:                                │  │
│ │ ├─ Moves up: -2px                          │  │
│ │ ├─ Shadow: 0 4px 12px rgba(0,102,255,0.3) │  │
│ │ └─ Smooth transition                        │  │
│ │                                              │  │
│ └─────────────────────────────────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Quick Reference Flowchart

```
START
  │
  ├─→ User visits app
  │
  ├─→ Check localStorage for authToken
  │
  ├─ Is token present?
  │  │
  │  ├─ NO  → Redirect to login.html ──→ User logs in ──→ Token stored
  │  │
  │  └─ YES → Load page normally ──→ Show Logout button
  │
  ├─→ User can navigate freely
  │
  ├─ User clicks Logout?
  │  │
  │  ├─ YES → Clear localStorage ──→ Redirect to login.html
  │  │
  │  └─ NO  → Continue using app
  │
  └─→ END
```

---

**Complete visual architecture of the DeepShield authentication system!** 🔐
