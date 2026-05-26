# 🚀 Complete Deployment Guide - Breathe ESG Platform

## ✅ Current Status

### Backend - COMPLETED
- ✅ **Service**: Running on Render
- ✅ **URL**: https://breathe-esg-api-tmp2.onrender.com
- ✅ **Database**: PostgreSQL with migrations
- ✅ **Health Check**: https://breathe-esg-api-tmp2.onrender.com/health/ → Returns `{"status": "ok"}`
- ✅ **API Endpoints**: All working
  - `/api/records/` - List emission records
  - `/api/records/summary/` - Dashboard summary stats
  - `/api/uploads/` - File upload endpoint

### Frontend - IN PROGRESS
- ⚠️ **Platform**: Vercel (needs reconfiguration)
- ⚠️ **URL**: https://breathe-esg.vercel.app
- ⚠️ **Status**: Build configuration not applied yet
- ✅ **Code**: Ready to deploy (all environment variables configured)

---

## 🔧 Fix Frontend Deployment on Vercel

The frontend code is ready, but Vercel needs to be manually configured to rebuild properly.

### Step 1: Go to Vercel Dashboard

1. Visit: https://vercel.com/dashboard
2. Log in with your GitHub account
3. Find project: `breathe-esg` (or similar name)
4. Click on the project to open it

### Step 2: Navigate to Settings

1. Click **Settings** tab (usually at top)
2. Click **General** in the left sidebar

### Step 3: Configure Root Directory

**IMPORTANT**: Set the Root Directory to your project root (not /frontend)

1. Look for "Root Directory" setting
2. It might be empty or set to `/`
3. **Leave it as is** (root of project)
4. Vercel should now recognize the `vercel.json` file

### Step 4: Check Environment Variables

1. Go to **Settings** → **Environment Variables**
2. Verify you have:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://breathe-esg-api-tmp2.onrender.com`
3. If missing, click **Add** and add it now
4. Click **Save**

### Step 5: Redeploy the Project

1. Go to **Deployments** tab
2. Find the latest failed/pending deployment
3. Click the **...** (three dots) button
4. Click **Redeploy**
5. Vercel will now:
   - Read the `vercel.json` configuration
   - Run `npm run build` from root
   - Build the React frontend in `frontend/` folder
   - Deploy to production

### Step 6: Monitor the Build

1. Watch the deployment logs
2. Wait for "Building..." → "Ready" (usually 3-5 minutes)
3. Once it shows "Ready", your app is live!

### Step 7: Test Your Frontend

Once deployment completes:

1. Go to: https://breathe-esg.vercel.app
2. Should see **"Breathe ESG"** header
3. Should show **Dashboard** with statistics
4. Should NOT show file listing anymore

---

## 📋 Configuration Files Prepared

Your repository now has:

### **vercel.json**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "frontend/build"
}
```
This tells Vercel to:
- Run `npm run build` at project root
- Look for built frontend in `frontend/build/` folder

### **package.json** (Root)
```json
{
  "private": true,
  "scripts": {
    "build": "cd frontend && npm run build"
  }
}
```
This defines the build script that vercel.json uses

### **.vercelignore**
```
backend
test_data
.git
.env.local
```
This prevents Vercel from uploading unnecessary files

### **frontend/.env.local**
```
REACT_APP_API_URL=https://breathe-esg-api-tmp2.onrender.com
```
This configures the React app to use your production backend

---

## 🔄 Complete System Architecture

```
┌─────────────────────────────────────────────────────┐
│         USER BROWSER                                │
│  (Desktop or Mobile)                                │
└──────────────────┬──────────────────────────────────┘
                   │
                   │ HTTPS
                   │
        ┌──────────▼──────────┐
        │  VERCEL CDN         │
        │  breathe-esg.       │
        │  vercel.app         │  ◄── Frontend (React)
        │  ┌────────────────┐ │
        │  │ React App      │ │
        │  │ - Dashboard    │ │
        │  │ - Upload       │ │
        │  │ - Records      │ │
        │  └────────┬───────┘ │
        └───────────┼──────────┘
                    │
                    │ API Calls
                    │ https://breathe-esg-api-
                    │ tmp2.onrender.com
                    │
        ┌───────────▼──────────────┐
        │  RENDER                  │
        │  breathe-esg-api-tmp2.   │
        │  onrender.com            │  ◄── Backend (Django)
        │  ┌────────────────────┐  │
        │  │ Python/Django      │  │
        │  │ Gunicorn Server    │  │
        │  │ - API Endpoints    │  │
        │  │ - Business Logic   │  │
        │  └────────┬───────────┘  │
        └───────────┼──────────────┘
                    │
                    │ SQL Queries
                    │
        ┌───────────▼──────────────┐
        │  POSTGRESQL DATABASE     │
        │  (Render Managed)        │  ◄── Data Storage
        │  ┌────────────────────┐  │
        │  │ emission_records   │  │
        │  │ companies          │  │
        │  │ audit_logs         │  │
        │  └────────────────────┘  │
        └──────────────────────────┘
```

---

## ✅ What Each Component Does

### Frontend (React on Vercel)
- **Location**: `frontend/` folder in your GitHub repo
- **Built**: On Vercel's servers when you deploy
- **Served**: Via Vercel's global CDN
- **Role**: User interface, form handling, data display
- **Connects to**: Backend API at `https://breathe-esg-api-tmp2.onrender.com`

### Backend (Django on Render)
- **Location**: `backend/` folder in your GitHub repo
- **Hosted**: Render.com
- **Running**: 24/7 Python application with Gunicorn
- **Role**: API endpoints, database operations, business logic
- **Database**: PostgreSQL managed by Render

### Database (PostgreSQL)
- **Hosted**: Render PostgreSQL
- **Tables**: `emission_records`, `companies`, `audit_logs`, etc.
- **Connection**: Backend connects via DATABASE_URL

---

## 🧪 Testing Your Deployment

### 1. Frontend is Live
Open: https://breathe-esg.vercel.app
- Should NOT show file listing
- Should show Breathe ESG app with Dashboard

### 2. Backend is Working
Open: https://breathe-esg-api-tmp2.onrender.com/health/
- Should return: `{"status": "ok", "message": "Django server is running", "database": "connected", ...}`

### 3. Frontend Connects to Backend
In browser, open DevTools (F12) → Network tab:
- Click Dashboard or Records tab
- Should see API request to `/api/records/summary/`
- Should return data with 200 status (no CORS errors)

---

## 🆘 Troubleshooting

### Problem: Vercel still shows file listing
**Solution**:
1. Double-check Root Directory setting (should be project root, not `/frontend`)
2. Make sure `vercel.json` is at project root (not in frontend folder)
3. Click "Redeploy" button in Vercel dashboard
4. Wait 3-5 minutes for build to complete

### Problem: React app loads but shows blank/error
**Solution**:
1. Open DevTools Console (F12)
2. Look for CORS or API errors
3. Verify `REACT_APP_API_URL` environment variable is set in Vercel
4. Check backend is online: https://breathe-esg-api-tmp2.onrender.com/health/

### Problem: "Cannot GET /" error
**Solution**:
1. Go to Vercel Deployments
2. Find the latest deployment
3. Click Redeploy
4. Make sure build succeeded (check logs)
5. Built app should be in `frontend/build/` folder

### Problem: CORS errors from frontend
**Solution**:
1. Backend CORS is already configured for all origins in production
2. If still getting CORS errors, check browser console for exact error
3. Might need to add Vercel domain to CORS whitelist

---

## 🎯 Final Checklist

- [ ] Vercel dashboard configured
- [ ] Root Directory set correctly
- [ ] Environment variable `REACT_APP_API_URL` added to Vercel
- [ ] Redeployed from Vercel dashboard
- [ ] Build completed successfully (check logs)
- [ ] Frontend displays at https://breathe-esg.vercel.app
- [ ] No file listing shown
- [ ] React app loads with Dashboard visible
- [ ] Backend health check returns data
- [ ] Console shows no errors

---

## 🚀 After Deployment Complete

### What to Test
1. **Upload Data**: Try uploading a test CSV file
2. **View Dashboard**: Should show record counts and CO₂ totals
3. **Review Records**: Browse uploaded emission records
4. **Approve Records**: Test the approval workflow

### Going Forward
- **Monitor Logs**: Check Render backend logs for errors
- **Check Vercel Analytics**: Monitor frontend performance
- **Database Backups**: Render handles automatic backups
- **Updates**: Just push to GitHub main branch → auto-deploys

---

## 📞 Support

If you encounter issues:

1. **Check Backend Health**: https://breathe-esg-api-tmp2.onrender.com/health/
2. **Check Vercel Build Logs**: Vercel Dashboard → Deployments → View Logs
3. **Check Browser Console**: F12 → Console for error messages
4. **Review GitHub Commits**: Verify all files are pushed correctly

---

## 🎉 Summary

✅ **Backend**: Running and accessible  
⏳ **Frontend**: Ready to deploy on Vercel (needs manual redeploy in dashboard)  
🔗 **Connected**: Both services configured to work together  

**Next Step**: Follow "Step 1-6" above to redeploy your frontend on Vercel!
