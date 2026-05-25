# Breathe ESG Backend

Django REST API for the ESG Data Ingestion & Audit Platform.

## Project Structure

```
backend/
├── breathe_esg/
│   ├── settings.py       # Django configuration (DB, apps, CORS)
│   ├── urls.py           # Main URL router
│   └── wsgi.py           # WSGI config
├── apps/
│   ├── companies/        # Multi-tenant company model
│   ├── uploads/          # Raw data ingestion
│   ├── records/          # Processed emission records
│   └── audit/            # Change audit trail
├── utils/
│   ├── parsers.py        # CSV/JSON parsing
│   ├── normalization.py  # Unit conversions (L, kWh, dates)
│   ├── emissions.py      # CO₂e calculations (fuel, electricity, flights)
│   ├── anomalies.py      # Suspicious data detection
│   ├── auditing.py       # Audit log creation
│   └── processor.py      # Master orchestrator (combines all steps)
├── manage.py             # Django CLI
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Installation & Setup

### 1. Prerequisites
- Python 3.14+
- PostgreSQL 18+
- pip (Python package manager)

### 2. Create Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database Connection
Edit `breathe_esg/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'breathe_esg',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Or use environment variables:
```bash
# Create .env file in backend/ folder
export DB_NAME=breathe_esg
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (for Django Admin)
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin
```

### 7. Start Server
```bash
python manage.py runserver
# Server starts at http://localhost:8000
# Admin at http://localhost:8000/admin
```

## API Endpoints

### Upload Endpoints

**POST /api/uploads/sap/**
- Upload SAP fuel consumption data (CSV)
- Body: FormData with `file` (CSV) and `company_id`
- Response: `{ records_created: 5, errors_count: 0, errors: [] }`

**POST /api/uploads/utility/**
- Upload utility/electricity data (CSV)
- Body: FormData with `file` (CSV) and `company_id`
- Response: Same as SAP

**POST /api/uploads/travel/**
- Upload business travel data (JSON)
- Body: FormData with `file` (JSON) and `company_id`
- Response: Same as SAP

### Records Endpoints

**GET /api/records/**
- List emission records with filtering
- Query params: `company_id`, `status` (PENDING/SUSPICIOUS/APPROVED/REJECTED), `scope` (SCOPE_1/2/3), `page`
- Response: Paginated list of EmissionRecord objects

**GET /api/records/:id/**
- Get single record details with audit history
- Response: Record object with nested `audit_history` array

**POST /api/records/:id/approve/**
- Approve or reject a record
- Body: `{ "status": "APPROVED|REJECTED", "anomaly_notes": "..." }`
- Response: Updated record object

**GET /api/records/summary/**
- Dashboard summary statistics
- Query params: `company_id`
- Response: `{ total_records, pending, suspicious, approved, rejected, total_co2e }`

## Data Processing Pipeline

### Step 1: Upload
- Raw file (CSV/JSON) received and stored in `RawDataIngest` table
- Original file content preserved for audit traceability

### Step 2: Parse
- CSV parsed using Python `csv.DictReader`
- JSON parsed using `json.loads()`
- Format-specific parsers extract required columns

### Step 3: Normalize
- **Volume:** 2500ml → 2.5L (using conversion factors)
- **Energy:** 0.5MWh → 500kWh
- **Date:** 20+ formats → ISO YYYY-MM-DD
- **Decimal:** Standardized to 2 decimal places

### Step 4: Calculate CO₂e
- **Fuel (Scope 1):** 1000L diesel × 2.68 = 2680 kg CO₂e
- **Electricity (Scope 2):** 5000kWh × 0.7 (global) = 3500 kg CO₂e
- **Flight (Scope 3):** Haversine distance × 0.12 kg/km = CO₂e

**Emission Factors:**
- Diesel: 2.68 kg/L
- Petrol: 2.31 kg/L
- Electricity (global): 0.7 kg/kWh
- Electricity (India): 0.82 kg/kWh
- Flight economy: 0.12 kg/km

### Step 5: Detect Anomalies
- Negative values → SUSPICIOUS
- Unknown units → SUSPICIOUS
- Spikes > 5x baseline → SUSPICIOUS
- Format validation errors → SUSPICIOUS

**Status Workflow:**
```
PENDING → [Analyst Review] → APPROVED (accepted)
   ↓
SUSPICIOUS (has anomalies) → [Analyst Review] → APPROVED or REJECTED
```

### Step 6: Audit
- All changes logged with:
  - Action (CREATED, FLAGGED, APPROVED, REJECTED, UPDATED)
  - Previous state (JSON)
  - New state (JSON)
  - Performed by (User)
  - Timestamp

## Database Models

### Company
- Multi-tenant model
- Fields: `id`, `name` (unique), `created_at`

### RawDataIngest
- Stores original uploaded file
- Fields: `company_fk`, `source_type` (SAP/UTILITY/TRAVEL), `original_filename`, `raw_payload` (text), `uploaded_at`

### EmissionRecord
- Processed, normalized emission data
- Fields: `company_fk`, `raw_data_ref_fk`, `scope_category`, `original_value/unit`, `normalized_value/unit`, `calculated_co2e`, `status`, `anomaly_notes`, `created_at/updated_at`
- Status: PENDING, SUSPICIOUS, APPROVED, REJECTED

### AuditLog
- Immutable change history
- Fields: `emission_record_fk`, `action`, `previous_state` (JSON), `new_state` (JSON), `performed_by_fk`, `timestamp`

## Utilities Explained

### parsers.py
- `parse_csv(text)` → list of dicts
- `parse_sap_csv(text)` → validates MANDT, WERKS, MENGE, MEINS, BUDAT
- `parse_utility_csv(text)` → validates MeterID, BillingStart, BillingEnd, kWh
- `parse_travel_json(text)` → validates from_airport, to_airport, date

### normalization.py
- `normalize_volume(value, unit)` → (normalized_value, "L")
- `normalize_energy(value, unit)` → (normalized_value, "kWh")
- `normalize_date(value)` → "YYYY-MM-DD"
- `normalize_decimal(value)` → Decimal with 2 places

### emissions.py
- `calculate_co2e_fuel(liters, fuel_type)` → kg CO₂e
- `calculate_co2e_electricity(kwh, region)` → kg CO₂e
- `calculate_co2e_flight(from_code, to_code, class)` → kg CO₂e
- `haversine_distance(lat1, lon1, lat2, lon2)` → km
- `identify_scope(activity_type)` → SCOPE_1/2/3

### anomalies.py
- `detect_anomalies(record_dict)` → (has_anomaly: bool, anomaly_list: list)
- Checks: negative values, missing fields, unknown units, spikes

### auditing.py
- `log_record_creation(record)` → creates AuditLog entry
- `log_record_flagged(record, anomalies)` → logs anomaly detection
- `log_record_approval(record, user, status, notes)` → logs approval
- `get_record_history(record)` → returns all AuditLog entries chronologically

### processor.py
- `process_sap_upload(RawDataIngest)` → parses, normalizes, calculates, detects anomalies, stores
- `process_utility_upload(RawDataIngest)` → same flow
- `process_travel_upload(RawDataIngest)` → same flow
- All return list of (success, record) tuples with error handling

## Testing

### Test Parse Functions
```python
from utils.parsers import parse_csv
data = parse_csv("col1,col2\nval1,val2")
print(data)  # [{'col1': 'val1', 'col2': 'val2'}]
```

### Test Normalization
```python
from utils.normalization import normalize_volume
norm_val, norm_unit = normalize_volume(2500, "ml")
print(f"{norm_val} {norm_unit}")  # 2.5 L
```

### Test Emissions
```python
from utils.emissions import calculate_co2e_fuel
co2e, desc = calculate_co2e_fuel(1000, "DIESEL")
print(f"{co2e} kg")  # 2680 kg
```

### Health Check
```bash
python manage.py check
# Output: System check identified no issues (0 silenced).
```

## Environment Variables

### Development (.env)
```
DB_NAME=breathe_esg
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
SECRET_KEY=your-secret-key
```

### Production (Render)
```
DB_NAME=breathe_esg_prod
DB_USER=postgres
DB_PASSWORD=[Render database password]
DB_HOST=[Render database host]
DB_PORT=5432
DEBUG=False
SECRET_KEY=[Generate via Django]
CORS_ALLOWED_ORIGINS=https://breathe-esg.vercel.app
```

## Deployment (Render)

1. Push code to GitHub
2. Create Render account
3. Create new PostgreSQL database on Render
4. Create new Web Service, connect GitHub repo
5. Set environment variables
6. Deploy
7. Test endpoints: `https://breathe-esg-api.render.com/api/records/`

## Common Issues

### "No such module named 'psycopg'"
- Solution: `pip install psycopg[binary]`

### Django apps not registered
- Solution: Use full app config paths in INSTALLED_APPS

### Migrations not found
- Solution: Create `migrations/` folder with `__init__.py`

### Port 8000 already in use
- Solution: `python manage.py runserver 8001`

## Support

For issues, check:
1. `python manage.py check` for system issues
2. Browser console for frontend errors
3. Django logs for backend errors
