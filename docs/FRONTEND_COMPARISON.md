# Frontend Comparison: Old vs New

This guide explains the differences between the old Vanilla JavaScript frontend and the new Vue.js frontend implementation.

---

## What Changed

### Old Frontend (Vanilla JavaScript)

- **URL:** `http://localhost:5000`
- **Technology:** Vanilla JavaScript served directly by Flask
- **Files:** `frontend/index.html` + `frontend/app.js`
- **Status:** Legacy implementation, replaced by Vue.js

### New Frontend (Vue.js with Vite)

- **URL:** `http://localhost:5173` (development mode)
- **Technology:** Vue.js 3 with Vite build tool
- **Files:** `frontend/src/` directory
- **Status:** Current active implementation

---

## Key Differences

### 1. Login Buttons

**Old Frontend:**
- Displayed in navbar when user is not authenticated
- Simple HTML with inline JavaScript

**New Frontend:**
- Same functionality - shows Login/Register buttons when not authenticated
- Component-based implementation with reactive state management
- **Location:** Top-right corner of navbar

### 2. Login with Wikimedia

**Old Frontend:**
- Available on login page
- Direct link to OAuth endpoint

**New Frontend:**
- Available on login page (`/login` route)
- Uses Vue Router for navigation
- **OAuth URL:** `http://localhost:5000/api/user/oauth/login` (unchanged)

### 3. Data Fetching

**Old Frontend:**
- Fetched directly from `/api/contest` endpoint
- Used Fetch API or XMLHttpRequest

**New Frontend:**
- Fetches from same `/api/contest` endpoint
- Uses Axios HTTP client with better error handling
- **Method:** Both versions use the same Flask API endpoints

### 4. OAuth Callback

**Old Frontend:**
- Redirected directly to Flask-served pages

**New Frontend:**
- Redirects to Vue.js app with `?oauth_success=true` query parameter
- Vue.js detects the parameter and updates authentication state
- **Callback URL:** `http://localhost:5000/api/user/oauth/callback` (unchanged)

---

## Usage Instructions

### Development Mode (Recommended)

Run both Flask and Vue.js servers separately for the best development experience.

#### Step 1: Start Flask Backend
```bash
cd backend
python app.py
```

Flask runs on: `http://localhost:5000`

#### Step 2: Start Vue.js Frontend
```bash
cd frontend
npm install  # Only needed the first time
npm run dev
```

Vue.js dev server runs on: `http://localhost:5173`

#### Step 3: Access the Application

- **Open:** `http://localhost:5173`
- Login buttons should appear in the navbar
- Click **"Login"** to see the **"Login with Wikimedia"** option

---

### Production Mode (Single Server)

Build the Vue.js frontend and serve it through Flask.

#### Step 1: Build Vue.js
```bash
cd frontend
npm run build
```

This creates optimized production files in the `dist/` directory.

#### Step 2: Start Flask
```bash
cd backend
python app.py
```

Flask automatically serves the built Vue.js files.

#### Step 3: Access the Application

- **Open:** `http://localhost:5000`
- Flask serves the built Vue.js files as static assets

## Troubleshooting

### Login Buttons Not Showing

If login buttons don't appear in the navbar:

1. Open browser DevTools (`F12`) and check the **Console** tab for errors
2. Verify Flask is running on `http://localhost:5000`
3. Verify Vue.js dev server is running on `http://localhost:5173`
4. Hard refresh the browser (`Ctrl+Shift+R` or `Cmd+Shift+R`)
5. Check if authentication state is loading correctly

### Data Not Loading

If contests or other data doesn't load:

1. Open the **Network** tab in DevTools
2. Verify API calls to `/api/contest` return `200 OK` status
3. Check Flask terminal for backend errors
4. Verify CORS is properly configured in Flask for `http://localhost:5173`
5. Ensure both servers are running

### OAuth Not Working

If OAuth authentication fails:

1. Verify OAuth consumer is registered with callback URL: `http://localhost:5000/api/user/oauth/callback`
2. Check Flask logs for OAuth-related errors
3. Verify cookies are being set (check **Application** tab → **Cookies** in DevTools)
4. Ensure `OAUTH_USE_OOB=False` in your `.env` file
5. Confirm the OAuth consumer is approved

---

## Migration Status

All features from the old Vanilla JavaScript frontend have been successfully migrated to Vue.js:

-   User authentication (login/register/logout)
-   Contest management (create/view/participate)
-   User dashboard with statistics
-   OAuth login with Wikimedia
-   API data fetching and display
-   All UI components and layouts

---

## Advantages of Vue.js Frontend

The new Vue.js implementation provides several improvements over the old frontend:

### Code Organization
- Component-based architecture for better maintainability
- Separation of concerns with single-file components
- Reusable UI components

### Development Experience
- Hot module replacement for instant updates
- Vue DevTools for debugging and inspection
- Modern ES6+ JavaScript features
- Better error messages and stack traces

### State Management
- Reactive data binding
- Centralized authentication state
- Automatic UI updates when data changes

### Performance
- Optimized production builds with code splitting
- Lazy loading of routes and components
- Smaller bundle sizes with tree-shaking

### Developer Tools
- Vue DevTools browser extension
- Component inspection and debugging
- Time-travel debugging for state changes

---

## Summary

The Vue.js frontend is a complete reimplementation of the original Vanilla JavaScript frontend with modern web development practices. All features have been migrated, and the new implementation offers better code organization, improved developer experience, and enhanced performance.

For daily development, use **Development Mode** with both servers running. For production deployment or testing the production build, use **Production Mode** with Flask serving the built Vue.js files.