# Pull Request Setup Guide

## Changes Made

This PR adds a login page to the ClutchCall application with the following features:

1. **New Login Component** (`components/Login.tsx`)
   - Dark blue background matching the design
   - Email and password input fields with icons
   - Password visibility toggle
   - "Forgot password?" link
   - "Sign In" button in teal color
   - "Sign up" link at the bottom

2. **Routing Setup**
   - Added `react-router-dom` dependency
   - Created `Dashboard` component (moved from App.tsx)
   - Set up routes: `/login` and `/dashboard`
   - Default route redirects to `/login`

3. **Updated Files**
   - `package.json` - Added react-router-dom dependency
   - `App.tsx` - Now handles routing
   - `components/Dashboard.tsx` - New component for the main betting interface
   - `components/Login.tsx` - New login page component

## To Create the Pull Request

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create a new branch:**
   ```bash
   git checkout -b feature/add-login-page
   ```

3. **Stage the changes:**
   ```bash
   git add .
   ```

4. **Commit the changes:**
   ```bash
   git commit -m "feat: Add login page with routing

   - Create Login component with email/password fields
   - Add react-router-dom for navigation
   - Set up routes for /login and /dashboard
   - Move main app content to Dashboard component
   - Add password visibility toggle
   - Style login page to match design specifications"
   ```

5. **Push to remote:**
   ```bash
   git push origin feature/add-login-page
   ```

6. **Create Pull Request:**
   - Go to your repository on GitHub/GitLab
   - Click "New Pull Request"
   - Select `feature/add-login-page` as the source branch
   - Select your main branch (usually `main` or `master`) as the target
   - Add a description and submit

## Testing

After installing dependencies, run:
```bash
npm run dev
```

Navigate to `http://localhost:5173` - you should see the login page.
Clicking "Sign In" will navigate to the dashboard.

