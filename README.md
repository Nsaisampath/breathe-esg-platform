# Breathe ESG - Emissions Tracking & Audit System

ESG emissions ingestion and analyst review platform. Companies upload data (SAP exports, utility bills, travel bookings) → system normalizes and calculates CO2e → analyst reviews flagged records → approves for reporting.

**Live**:
- Frontend: https://breathe-esg-platform-hem2rufgv-nsaisampaths-projects.vercel.app/
- Backend API: https://breathe-esg-api-tmp2.onrender.com

---

## Setup

**Backend** (Django + PostgreSQL):
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend** (React):
```bash
cd frontend
npm install
npm start
```

API: `http://localhost:8000/api/`  
Frontend: `http://localhost:3000`

---

## Data Sources

Three formats supported:

1. **SAP CSV** (MANDT, WERKS, MENGE, MEINS, BUDAT) → Fuel consumption → Scope 1
2. **Utility CSV** (MeterID, BillingStart, BillingEnd, kWh) → Electricity → Scope 2
3. **Travel JSON** (from_airport, to_airport, cabin_class) → Flight distance → Scope 3

All normalized to: liters (fuel), kWh (energy), km (distance), kg CO2e (emissions)

---

## Architecture

**Three-layer data model**:
```
RawDataIngest (immutable original)
    ↓
EmissionRecord (normalized + calculated CO2e)
    ↓
AuditLog (approval history)
```

Why three layers?
- RawDataIngest: Regulatory audit trail (keep originals forever)
- EmissionRecord: Analysis-ready with full traceability
- AuditLog: Track who approved what and when

---

## Key Features

- **Anomaly Detection**: Flags negatives, missing fields, unknown units, 5x spikes, source-specific limits
- **CO2e Calculation**: IPCC/EPA factors with regional grids (India 0.82, EU 0.38, Global 0.70 kg CO2e/kWh)
- **Flight Distance**: Haversine formula from airport coordinates
- **Approval Workflow**: PENDING → review → APPROVED/REJECTED
- **Dashboard**: Scope 1/2/3 breakdown, pending/approved/rejected counts
- **Multi-Tenant**: Company-scoped data isolation

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/records/` | List records with filtering |
| GET | `/api/records/{id}/` | Record details + audit history |
| GET | `/api/records/summary/` | Dashboard stats |
| POST | `/api/records/{id}/approve/` | Approve/reject record |
| POST | `/api/uploads/sap/` | Upload SAP CSV |
| POST | `/api/uploads/utility/` | Upload utility CSV |
| POST | `/api/uploads/travel/` | Upload travel JSON |
| GET | `/health/` | Backend status |

---

## Sample Data

Three realistic datasets in `backend/`:

1. `sample_data_utility.csv` - 9 meter records with seasonal spike (flagged suspicious)
2. `sample_data_travel.json` - 10 flights, economy/business mix

Upload via frontend to see records process, anomalies flagged, then approve.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 6.0.5 + DRF 3.14.0 + PostgreSQL 18.1 |
| Frontend | React 18.2.0 + Tailwind CSS 3.3.6 |
| Server | Gunicorn 26.0 (Render) |
| Hosting | Render (backend) + Vercel (frontend) |

---

## Code Structure

```
backend/
  apps/
    records/ → EmissionRecord + APIs
    uploads/ → RawDataIngest + upload
    audit/ → AuditLog
    companies/ → Multi-tenancy
  utils/
    processor.py → Parse → normalize → validate
    emissions.py → CO2e + Haversine
    anomalies.py → Anomaly detection
    parsers.py → CSV/JSON parsing

frontend/
  pages/
    Dashboard.js → Stats
    UploadPage.js → File upload
    RecordsPage.js → List + filter
    ReviewPage.js → Detail + approval
  services/
    api.js → Axios client
```

---

## Design Decisions

- **Immutable raw data**: Store originals forever (regulatory requirement)
- **Scope auto-detect**: Fuel→Scope1, Electricity→Scope2, Travel→Scope3
- **Regional factors**: Electricity varies by grid (0.38–0.82 kg CO2e/kWh)
- **Haversine distance**: Calculate flight km from airport coordinates
- **Source-specific limits**: Flight max 15,000km, energy max 1M kWh/month
- **Multi-tenant**: company_id filters all queries

See [MODEL.md](MODEL.md), [DECISIONS.md](DECISIONS.md), [TRADEOFFS.md](TRADEOFFS.md), [SOURCES.md](SOURCES.md).

---

## Emission Factors (Verified)

| Source | Factor | Reference |
|--------|--------|-----------|
| Diesel | 2.68 kg CO2e/L | IPCC AR5 |
| Petrol | 2.31 kg CO2e/L | IPCC AR5 |
| Electricity (India) | 0.82 kg CO2e/kWh | CEA 2024 |
| Electricity (Global) | 0.70 kg CO2e/kWh | IEA |
| Flight (economy) | 0.12 kg CO2e/km | ICAO |
| Flight (business) | 0.27 kg CO2e/km | Atmosfair |
