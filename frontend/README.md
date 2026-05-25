# Breathe ESG Frontend

React.js frontend for the ESG Data Ingestion & Audit Platform.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable React components
│   ├── pages/            # Page-level components
│   │   ├── Dashboard.js  # Stats dashboard
│   │   ├── UploadPage.js # File upload interface
│   │   ├── RecordsPage.js # Records table with filtering
│   │   └── ReviewPage.js # Individual record review/approval
│   ├── services/
│   │   └── api.js        # Axios API client
│   ├── App.js            # Main app routing
│   ├── index.js          # React entry point
│   └── index.css         # Global Tailwind styles
├── public/
│   └── index.html        # HTML template
├── package.json          # Dependencies
├── tailwind.config.js    # Tailwind CSS config
├── postcss.config.js     # CSS processing
└── .env.example          # Environment variables template
```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env.local`:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local to set REACT_APP_API_URL=http://localhost:8000/api
   ```

3. **Start development server:**
   ```bash
   npm start
   ```
   - Opens at http://localhost:3000
   - Hot reload enabled (changes auto-refresh)

4. **Build for production:**
   ```bash
   npm run build
   ```
   - Creates optimized build in `build/` folder

## Pages Explained

### Dashboard
- **Path:** `/`
- **Shows:** Summary statistics (total records, pending, suspicious, approved, CO₂e total)
- **Purpose:** High-level overview of ESG data status
- **Calls:** `GET /api/records/summary/`

### Upload Page
- **Path:** `/upload`
- **Shows:** Three upload options (SAP/Utility/Travel) with format guides
- **Purpose:** Ingest raw ESG data from enterprise systems
- **Calls:** `POST /api/uploads/sap/`, `/api/uploads/utility/`, `/api/uploads/travel/`
- **Handles:** File validation, error display, success confirmation

### Records Page
- **Path:** `/records`
- **Shows:** Paginated table of all emission records with filtering
- **Filters:** By status (Pending/Suspicious/Approved/Rejected) and scope (1/2/3)
- **Purpose:** Browse and search processed emission records
- **Calls:** `GET /api/records/`

### Review Page
- **Path:** `/records/:id/review`
- **Shows:** Full record details, anomaly flags, original vs normalized values, CO₂e calculation
- **Purpose:** Analyst reviews suspicious records and approves/rejects
- **Calls:** `GET /api/records/{id}/`, `POST /api/records/{id}/approve/`

## Key Features

### API Service (src/services/api.js)
- Centralized Axios client with base URL from `.env`
- Organized by domain: `recordsAPI`, `uploadsAPI`
- Error handling passed to components
- Supports FormData for file uploads

### Styling (Tailwind CSS)
- **Colors:** 
  - `breathe-primary` (dark slate) for headers
  - `breathe-accent` (green) for CTA buttons
  - `breathe-warning`/`breathe-danger` for alerts
- **Components:**
  - `.card` - Reusable card container
  - `.btn-primary` / `.btn-secondary` / `.btn-danger` - Button variants
  - `.badge` - Status badges (pending/suspicious/approved/rejected)
  - `.form-input` / `.form-label` - Form elements
  - `.alert-*` - Alert messages

### React Hooks Used
- **useState:** Component state management
- **useEffect:** Data fetching on mount/dependency change
- **useParams:** Extract URL parameters (e.g., record ID)
- **useNavigate:** Programmatic navigation

## Environment Variables

**Development (.env.local):**
```
REACT_APP_API_URL=http://localhost:8000/api
```

**Production (set in deployment):**
```
REACT_APP_API_URL=https://breathe-esg-api.render.com/api
```

## Common Issues

### CORS errors
- Ensure backend has `CORS_ALLOWED_ORIGINS` configured
- Check `django-cors-headers` installed in Django

### API calls failing
- Verify backend server is running: `python manage.py runserver`
- Check `.env.local` has correct API_URL
- Check browser console for error messages

### Styling issues
- Run `npm run build` if Tailwind classes not showing
- Restart dev server after changing `tailwind.config.js`

## Testing Locally

1. Start backend: `python manage.py runserver`
2. Start frontend: `npm start`
3. Upload test file: Go to Upload page, select format
4. View records: Go to Records page, see uploaded data
5. Review: Click "Review" on a record, approve/reject

## Deployment

- **Frontend to Vercel:** `vercel deploy` (with `REACT_APP_API_URL` env var)
- **Backend to Render:** See [backend README](../backend/README.md)
