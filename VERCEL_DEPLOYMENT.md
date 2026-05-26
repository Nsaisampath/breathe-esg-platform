# Frontend Deployment Guide - Vercel

## ✅ Frontend Configuration Status

The frontend has been configured correctly for production deployment:

- ✅ API URL uses environment variable: `REACT_APP_API_URL`
- ✅ Backend URL set to: `https://breathe-esg-api-tmp2.onrender.com`
- ✅ No localhost URLs in production code
- ✅ All API endpoints configured correctly

## Step 1: Prepare GitHub (Already Done)

Your code is already in GitHub repository:
- **Repository**: `https://github.com/Nsaisampath/breathe-esg-platform`
- **Branch**: `main`
- **Frontend location**: `/frontend`

## Step 2: Deploy to Vercel

### Option A: Vercel Dashboard (Easiest)

1. **Go to Vercel.com**
   - Visit: https://vercel.com
   - Sign in with GitHub account (or create one)

2. **Import Your Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Find and select: `breathe-esg-platform`
   - Click "Import"

3. **Configure Build Settings**

   When Vercel shows configuration screen:

   - **Project Name**: `breathe-esg` (or your choice)
   - **Root Directory**: Select `frontend` (IMPORTANT!)
   - **Framework**: Should auto-detect as "Create React App"
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `build` (default)

4. **Add Environment Variables**

   Before clicking "Deploy", add environment variables:

   - Click "Environment Variables"
   - Add new variable:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://breathe-esg-api-tmp2.onrender.com`
   - Click "Add"

5. **Deploy**
   - Click "Deploy" button
   - Wait for deployment to complete (~2-3 minutes)

6. **Get Your Frontend URL**
   - After deployment completes, you'll get a URL like:
     `https://breathe-esg.vercel.app`
   - This is your production frontend!

### Option B: Vercel CLI (For experienced users)

If you prefer command line:

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to project root
cd path/to/breathe-esg-platform

# Deploy
vercel

# During setup:
# - Set project name
# - Link to your GitHub account
# - Set root directory to: frontend
# - Accept default build settings
# - Add REACT_APP_API_URL environment variable
```

## Step 3: Verify Frontend Deployment

Once deployed, test the frontend:

1. **Open your Vercel URL** (e.g., `https://breathe-esg.vercel.app`)

2. **Test Dashboard**
   - Should load without errors
   - Should display: "Loading dashboard..." then show stats

3. **Test API Connectivity**
   - Dashboard should fetch data from backend
   - Stats should display: 0 records (no data uploaded yet)

4. **Check Browser Console**
   - Open DevTools (F12)
   - Go to Console tab
   - Should see no CORS errors (backend allows requests from Vercel)

## Frontend Architecture

```
breathe-esg-platform/
├── backend/
│   ├── breathe_esg/
│   │   ├── settings.py      (Production config)
│   │   ├── urls.py          (API routes)
│   │   ├── wsgi.py          (Gunicorn entry)
│   │   └── ...
│   └── apps/
│       ├── records/         (API endpoints)
│       ├── uploads/
│       └── audit/
│
├── frontend/                 ← Deployed to Vercel
│   ├── src/
│   │   ├── services/api.js   (API client - uses REACT_APP_API_URL)
│   │   ├── pages/            (Dashboard, Upload, Records)
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   ├── .env.example          (Shows required variables)
│   └── tailwind.config.js    (Styling)
│
└── Procfile                   (Render config for backend)
```

## Environment Variables Summary

| Variable | Frontend | Value |
|----------|----------|-------|
| `REACT_APP_API_URL` | Vercel | `https://breathe-esg-api-tmp2.onrender.com` |

## CORS Configuration

The backend Django is already configured to accept requests from Vercel:

✅ CORS is enabled for all origins in production mode
✅ Frontend can make requests to backend API

## Deployment Checklist

- [x] Frontend API configuration uses environment variables
- [x] Backend URL set to production (https://breathe-esg-api-tmp2.onrender.com)
- [x] No localhost URLs in production code
- [x] Environment variables configured in .env files
- [x] GitHub repository ready for Vercel deployment
- [ ] Deploy to Vercel (follow Steps 1-3 above)
- [ ] Test frontend at Vercel URL
- [ ] Verify API calls work

## Troubleshooting

### "CORS Error" in browser console
- Check that REACT_APP_API_URL is set correctly in Vercel dashboard
- Verify backend CORS settings in Django

### "API returns 404"
- Ensure backend URL doesn't have `/api` at the end (api.js adds it)
- Check that records table exists: `https://breathe-esg-api-tmp2.onrender.com/health/`

### "Deployment fails"
- Ensure Root Directory is set to `frontend`
- Build Command should be: `npm run build`
- Output Directory should be: `build`

### "Page shows blank"
- Check browser console for errors (F12)
- Verify environment variables in Vercel dashboard
- Check that backend is online

## Next Steps After Deployment

1. **Test end-to-end workflow**
   - Upload data via frontend
   - View data in dashboard
   - Approve/review records

2. **Monitor**
   - Check Vercel analytics
   - Monitor backend logs at Render

3. **Custom Domain** (Optional)
   - Add custom domain to Vercel project
   - Update backend CORS to accept new domain

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **React Deployment**: https://create-react-app.dev/deployment/
- **Vercel CLI**: https://vercel.com/cli
