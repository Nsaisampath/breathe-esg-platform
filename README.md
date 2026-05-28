# Breathe ESG - Emissions Tracking & Audit Platform

A realistic ESG emissions ingestion, normalization, and analyst review system. Built to demonstrate how companies can track Scope 1, 2, and 3 emissions with automated anomaly detection and full audit trails.

**Live Deployment**:
- Backend API: https://breathe-esg-api-tmp2.onrender.com
- Frontend: https://breathe-esg.vercel.app

---

## Overview

Breathe ESG solves a real problem: Companies have messy ESG data scattered across multiple systems (SAP ERP, utility billing, travel bookings). This system ingests data from all three sources, normalizes it to standard units, calculates CO2e emissions, flags suspicious records, and maintains a complete audit trail.

**Key Capability**: Upload a CSV file → System automatically processes → Analyst reviews flagged anomalies → Approves for reporting

---

## Quick Start

### For Analysts

1. **Access the dashboard**: https://breathe-esg.vercel.app
2. **View current emissions**: Dashboard shows Scope 1/2/3 breakdown
3. **Upload new data**: Upload SAP CSV, utility CSV, or travel JSON
4. **Review flagged records**: System highlights suspicious data for manual review
5. **Approve records**: Click to approve → included in totals
6. **View audit history**: See who approved what, when

### For Developers

```bash
# Clone repository
git clone https://github.com/Nsaisampath/breathe-esg-platform.git
cd breathe-esg-platform

# Backend setup (Django + PostgreSQL)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (React)
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

---

## Data Sources Supported

### 1. SAP ERP (Fuel/Procurement)
Track company vehicle fuel consumption and procurement from SAP exports.

**Format**:
```csv
MANDT,WERKS,MENGE,MEINS,BUDAT
100,1001,2500,L,2024-01-15
100,1001,1500,L,2024-01-16
```

**Normalized to**: Liters → kg CO2e
**Scope**: Scope 1 (Direct emissions)
**Emission factors**: Diesel 2.68, Petrol 2.31, LPG 1.53 kg CO2e/L

### 2. Utility Billing (Electricity)
Track facility electricity consumption from billing invoices.

**Format**:
```csv
MeterID,BillingStart,BillingEnd,kWh
MTR-001,2024-01-01,2024-01-31,5000
MTR-002,2024-01-01,2024-01-31,8500
```

**Normalized to**: kWh (already standardized)
**Scope**: Scope 2 (Indirect energy)
**Emission factors**: Global 0.7, India 0.82, EU 0.38 kg CO2e/kWh

### 3. Travel Bookings (Business Travel)
Track employee flight bookings with airport codes and cabin class.

**Format**:
```json
[
  {
    "employee": "Raj Kumar",
    "from_airport": "DEL",
    "to_airport": "BLR",
    "date": "2024-01-15",
    "cabin_class": "economy"
  }
]
```

**Normalized to**: km (calculated from airport coordinates) → kg CO2e  
**Scope**: Scope 3 (Indirect other - employee travel)
**Emission factors**: Economy 0.12, Business 0.27, First 0.35 kg CO2e/km

---

## Architecture

### Three-Layer Data Model

```
Raw Data Upload
    ↓ (parse)
RawDataIngest (immutable copy)
    ↓ (process)
EmissionRecord (normalized + calculated)
    ↓ (review)
AuditLog (track approval)
```

**Why three layers?**
1. **RawDataIngest**: Regulatory requirement - keep original files forever
2. **EmissionRecord**: Analysis-ready data with source traceability
3. **AuditLog**: Compliance audit trail

See [MODEL.md](MODEL.md) for detailed architecture explanation.

---

## Key Features

### ✅ Multi-Source Ingestion
- SAP CSV (messy real-world data)
- Utility billing CSV
- Travel JSON (airport codes)
- Extensible to any format

### ✅ Automatic Normalization
- All volumes → liters
- All energy → kWh
- All distances → km
- All emissions → kg CO2e

### ✅ Realistic Anomaly Detection
- Negative values (physical impossibility)
- Missing required fields
- Unknown units
- Extreme spikes (>5x baseline)
- Source-specific checks (flight distance, energy consumption limits)

### ✅ Accurate Emissions Calculation
- IPCC AR5 emission factors
- EPA approved methodology
- Regional electricity grids (India, EU, UK, US, Global)
- Cabin class tracking (economy vs business)
- Haversine flight distance calculation

### ✅ Full Audit Trail
- Every record creation logged
- Every approval/rejection logged
- Who did it, when, with what notes
- Previous state snapshots for forensics

### ✅ Scope 1/2/3 Categorization
- Scope 1: Direct (fuel, fleet)
- Scope 2: Indirect energy (purchased electricity)
- Scope 3: Other indirect (travel, supply chain)

### ⚠️ Basic but Functional UI
- Dashboard with status cards
- Upload form with format guides
- Records list with filtering
- Review page with anomaly details
- NOT production-polished (MVP)

---

## API Endpoints

### Records
- **GET `/api/records/`** - List all emission records with filtering
- **GET `/api/records/{id}/`** - Get full details of one record
- **GET `/api/records/summary/`** - Dashboard summary stats
- **POST `/api/records/{id}/approve/`** - Approve or reject record

### Upload
- **POST `/api/uploads/sap/`** - Upload SAP CSV
- **POST `/api/uploads/utility/`** - Upload utility CSV
- **POST `/api/uploads/travel/`** - Upload travel JSON

### System
- **GET `/health/`** - Backend health + database status

Example:
```bash
# Get summary
curl https://breathe-esg-api-tmp2.onrender.com/api/records/summary/

# Response
{
  "total_records": 16,
  "pending": 15,
  "suspicious": 0,
  "approved": 1,
  "rejected": 0,
  "total_co2e": 41916.31
}
```

---

## Sample Data

Three complete realistic datasets included:

1. **SAP Fuel Data** (`backend/sample_data_sap.csv`):
   - 5 fuel records
   - Mix of diesel/petrol
   - Includes one negative value (stock return) - flagged suspicious

2. **Utility Electricity** (`backend/sample_data_utility.csv`):
   - 9 meter records across 4 months
   - Includes seasonal variation spike - flagged suspicious

3. **Travel Flights** (`backend/sample_data_travel.json`):
   - 10 flight bookings
   - Mix of economy/business class
   - Real Indian airport codes (DEL, BLR, BOM, MAA, HYD)

**To test**:
```bash
# 1. Access frontend
https://breathe-esg.vercel.app

# 2. Upload sample data from backend/sample_data_*

# 3. See records processed and flagged in dashboard

# 4. Click into SUSPICIOUS records to see why flagged

# 5. Approve or reject each record
```

---

## Technology Stack

### Backend
- **Django 6.0.5** - Web framework
- **Django REST Framework 3.14.0** - API builder
- **PostgreSQL 18.1** - Database
- **Gunicorn 26.0.0** - WSGI server
- **Python 3.11**

### Frontend
- **React 18.2.0** - UI framework
- **React Router DOM 6.20.0** - Routing
- **Axios 1.6.2** - HTTP client
- **Tailwind CSS 3.3.6** - Styling
- **Create React App** - Build tool

### Deployment
- **Backend**: Render.com (Django app + PostgreSQL)
- **Frontend**: Vercel (React static hosting)
- **Database**: Render managed PostgreSQL

---

## Documentation

- **[MODEL.md](MODEL.md)** - Data architecture, why three layers, how it works
- **[DECISIONS.md](DECISIONS.md)** - Why we chose SAP/Utility/Travel formats, Haversine for flights, etc.
- **[TRADEOFFS.md](TRADEOFFS.md)** - What we intentionally didn't build and why
- **[SOURCES.md](SOURCES.md)** - Real-world research, emission factors, data validation

Read these to understand the design philosophy.

---

## How It Works: Real Example

**Scenario**: Company uploads 100 L of diesel fuel consumed on 2024-01-15

### Step 1: Ingest
```
POST /api/uploads/sap/
Body: 
  company_id: 1
  filename: "january-fuel.csv"
  file_content: "MANDT,WERKS,MENGE,MEINS,BUDAT\n100,1000,100,L,2024-01-15"
```

### Step 2: Parse & Store Raw Data
```python
RawDataIngest.objects.create(
  company_id=1,
  source_type='SAP',
  original_filename='january-fuel.csv',
  raw_payload='[full CSV text]'  # Immutable copy
)
```

### Step 3: Process
```python
# Extract
plant = "1000"
quantity = 100
unit = "L"

# Normalize (already in liters)
normalized_value = 100
normalized_unit = "L"

# Identify scope
scope = "SCOPE_1"  # Direct fuel

# Calculate CO2e
co2e = 100 * 2.68 = 268 kg CO2e

# Check anomalies
anomalies = []  # No anomalies (positive, valid unit, reasonable value)

# Create record
EmissionRecord.objects.create(
  company=company,
  activity_type="Plant 1000 Fuel Consumption",
  scope_category="SCOPE_1",
  original_value=100, original_unit="L",
  normalized_value=100, normalized_unit="L",
  calculated_co2e=268,
  status="PENDING",  # Ready for review
  anomaly_notes=""
)
```

### Step 4: Log Creation
```python
AuditLog.objects.create(
  action="CREATED",
  new_state={"status": "PENDING", "co2e": 268},
  performed_by=None  # System created it
)
```

### Step 5: Analyst Review
Analyst sees in dashboard:
- 1 new PENDING record
- Clicks into it
- Sees: 100 L diesel → 268 kg CO2e
- Can see original SAP values
- Approves it

### Step 6: Log Approval
```python
AuditLog.objects.create(
  action="APPROVED",
  previous_state={"status": "PENDING"},
  new_state={"status": "APPROVED"},
  performed_by=analyst_user
)
```

Result: Record contributes 268 kg CO2e to dashboard totals ✅

---

## Analyst Workflow

1. **Dashboard** - See total CO2e, count by status
2. **Upload** - Submit new CSV or JSON file
3. **View Records** - See all uploaded records with status
4. **Review** - Click into SUSPICIOUS records to understand why flagged
5. **Approve/Reject** - Mark record as OK or bad
6. **Export** (future) - Generate TCFD/SEC report

---

## What's Realistic vs MVP

### ✅ Production-Quality
- Emission factor accuracy (IPCC/EPA standards)
- Flight distance calculation (Haversine ±1%)
- Anomaly detection logic (catches real problems)
- Audit trail (regulatory requirement)
- Multi-tenant separation (company_id filtering)

### ⚠️ MVP / Simplified
- Only 15 airports (can expand)
- No real-time data (batch processing)
- No user authentication (company_id in request)
- Basic UI (functional, not beautiful)
- No complex approval workflows

### ❌ Future Work
- Scope 3 supply chain tracking
- ML-based anomaly detection
- Hotel + ground transport tracking
- Integration with TCFD reporting standards
- Mobile app
- Real-time meter API integration

See [TRADEOFFS.md](TRADEOFFS.md) for full trade-offs analysis.

---

## Development

### Running Locally

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # Runs on http://localhost:8000
```

**Frontend**:
```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

API will be at `http://localhost:8000/api/`
Frontend will hit `http://localhost:8000` for API calls

### Testing

**Backend health**:
```bash
curl http://localhost:8000/health/
```

**Sample data**:
```bash
# Upload SAP data
curl -X POST http://localhost:8000/api/uploads/sap/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "filename": "fuel.csv",
    "file_content": "MANDT,WERKS,MENGE,MEINS,BUDAT\n100,1000,2500,L,2024-01-15"
  }'
```

---

## Project Structure

```
breathe-esg-platform/
├── backend/
│   ├── apps/
│   │   ├── records/        # EmissionRecord model + API
│   │   ├── uploads/        # RawDataIngest + upload endpoints
│   │   ├── audit/          # AuditLog model
│   │   └── companies/      # Multi-tenancy
│   ├── utils/
│   │   ├── processor.py    # Core processing pipeline
│   │   ├── parsers.py      # CSV/JSON parsing
│   │   ├── normalization.py # Unit conversion
│   │   ├── emissions.py    # CO2e calculation
│   │   ├── anomalies.py    # Anomaly detection
│   │   └── auditing.py     # Audit logging
│   ├── sample_data_*.csv   # Test data
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── pages/          # Dashboard, Upload, Records, Review
│   │   ├── components/     # Reusable UI components
│   │   ├── services/       # API client
│   │   └── App.js          # Main router
│   └── package.json
├── MODEL.md                 # Data architecture
├── DECISIONS.md            # Design rationale
├── TRADEOFFS.md            # What we didn't build
├── SOURCES.md              # Research + real-world data
├── README.md               # This file
├── Procfile                # Deployment config
└── vercel.json             # Frontend deployment config
```

---

## Deployment

### Backend (Render)
```bash
# Procfile
web: cd backend && python manage.py migrate --noinput && gunicorn breathe_esg.wsgi

# Environment variables
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=breathe-esg-api-tmp2.onrender.com
SECRET_KEY=[random key]
DEBUG=False
CORS_ALLOWED_ORIGINS=https://breathe-esg.vercel.app
```

### Frontend (Vercel)
```bash
# vercel.json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/build"
}

# Environment variables
REACT_APP_API_URL=https://breathe-esg-api-tmp2.onrender.com
```

---

## Common Issues

**Q: Frontend shows directory listing instead of app**
A: Vercel deployment issue. Check vercel.json configuration and build logs.

**Q: API returns 404**
A: Verify backend is running and ALLOWED_HOSTS includes your domain.

**Q: CORS errors**
A: Check CORS_ALLOWED_ORIGINS in backend settings.

**Q: Records not saving**
A: Check PostgreSQL connection. Run `python manage.py migrate` to create tables.

**Q: Anomaly detection not working**
A: Check utils/anomalies.py. Make sure record_data has required fields.

---

## Support

- **Issues**: GitHub issues
- **Deployment**: Render + Vercel dashboards
- **Documentation**: See MODEL.md, DECISIONS.md, TRADEOFFS.md, SOURCES.md

---

## License

Built as an internship project. Code is provided as-is for educational purposes.

---

## Next Steps for Production

1. **Add authentication** (5 days) - Login system, role-based access
2. **Improve UX** (3-5 days) - Dashboard design, data visualization
3. **Add export** (3 days) - Generate TCFD/GRI reports
4. **Performance tuning** (2-3 days) - Optimize for large datasets
5. **Compliance audit** (5 days) - Third-party verification of calculations

See [TRADEOFFS.md](TRADEOFFS.md) for full prioritization.

---

**Built with realistic ESG domain expertise. Every emission factor, every anomaly check, every data format is based on actual research and real-world problems.**
