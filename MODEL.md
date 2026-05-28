# Data Architecture Model

## Overview

Breathe ESG implements a realistic ESG emissions ingestion and audit system with three-layer architecture:

1. **Raw Ingest Layer** - Original, untouched data as uploaded
2. **Normalized Emission Records** - Standardized, calculated emissions ready for analysis
3. **Audit Trail** - Complete history of changes and approvals

## Why This Architecture?

### Immutable Source of Truth
- Keep raw data unchanged → enables re-processing if logic changes
- Regulatory compliance: auditors can trace back to original uploads
- Debugging: can investigate discrepancies between raw and normalized

### Normalized Emission Records
- All volumes standardized to liters
- All energy standardized to kWh  
- All distances standardized to kilometers
- All emissions calculated to kg CO2e
- Enables fair comparison across upload sources and time periods

### Audit Tracking
- Every change to a record is logged
- Who approved it, when, with what notes
- Compliance requirement for regulatory submissions
- Accountability for data stewardship

## Data Models

### RawDataIngest
```python
company_id          # Which company uploaded this
source_type         # SAP, UTILITY, or TRAVEL
original_filename   # What the file was called
raw_payload         # The actual file content (CSV or JSON text)
uploaded_at         # Timestamp
```

**Purpose**: Immutable record of exactly what was uploaded

### EmissionRecord
```python
company_id              # Which company this record belongs to
raw_data_ref            # Link back to original upload
activity_type           # "Fuel Consumption", "Electricity Usage", etc
scope_category          # SCOPE_1, SCOPE_2, or SCOPE_3

# Original values
original_value          # As received from upload
original_unit           # L, kWh, km, etc

# Normalized values
normalized_value        # After unit conversion
normalized_unit         # Standard unit

# Calculated results
calculated_co2e         # kg CO2e (regulatory standard unit)

# Status & notes
status                  # PENDING, SUSPICIOUS, APPROVED, REJECTED
anomaly_notes          # Why it was flagged if suspicious

created_at, updated_at  # Timestamps
```

**Purpose**: Analysis-ready emissions data with source traceability

### AuditLog
```python
emission_record         # Which record changed
action                  # CREATED, FLAGGED, APPROVED, REJECTED, UPDATED
previous_state          # JSON snapshot before change
new_state              # JSON snapshot after change
performed_by           # Who made the change (null = system)
timestamp              # When change occurred
```

**Purpose**: Complete change history for compliance and debugging

## Processing Pipeline

### 1. Ingestion
```
File upload
    ↓
Parse (CSV or JSON)
    ↓
Create RawDataIngest
```

### 2. Normalization & Validation
```
For each row:
    ↓
Extract values & units
    ↓
Normalize to standard units
    ↓
Check for anomalies
    ↓
Calculate CO2e
```

### 3. Storage & Review
```
Create EmissionRecord
    ↓
If anomalies found → status = SUSPICIOUS
    ↓
Create AuditLog entry
    ↓
Analyst can APPROVE or REJECT
```

### 4. Audit Trail
```
When analyst approves:
    ↓
Update record status
    ↓
Record who approved, when, with what notes
    ↓
Create new AuditLog entry
```

## Multi-Tenancy

Records belong to Companies:
- Each upload is linked to a company
- Each emission record is linked to a company
- API filters automatically by company context

This ensures:
- Data isolation between organizations
- Clear ownership and accountability
- Scalability for multiple clients

## Scope Categorization

The system categorizes all emissions into three scopes per GHG Protocol:

### Scope 1: Direct Emissions
- Fuel combustion in company-owned vehicles
- On-site generation (e.g., diesel generators)
- **Uploaded via**: SAP procurement data
- **Normalized to**: Liters → kg CO2e

### Scope 2: Indirect Energy
- Purchased electricity
- Purchased steam/heating
- **Uploaded via**: Utility billing data
- **Normalized to**: kWh → kg CO2e
- **Region-specific factors**: INDIA, EU, UK, US, GLOBAL

### Scope 3: Other Indirect
- Business travel (flights, hotels, ground transport)
- Supply chain emissions
- **Uploaded via**: Travel data
- **Normalized to**: km → kg CO2e
- **Cabin class tracking**: ECONOMY, BUSINESS, FIRST

## Emission Factor Standards

All factors based on:
- **IPCC AR5** (Intergovernmental Panel on Climate Change)
- **EPA Guidelines** (US Environmental Protection Agency)
- **UK Government Emission Factors**

Examples:
- Diesel: 2.68 kg CO2e/liter
- Electricity (Global avg): 0.7 kg CO2e/kWh
- Electricity (India): 0.82 kg CO2e/kWh (coal-heavy grid)
- Flight (Economy): 0.12 kg CO2e/km per passenger

## Anomaly Detection

Flags suspicious records for manual review:

1. **Negative values** - Physical impossibility
2. **Missing fields** - Data quality issue
3. **Unknown units** - Can't calculate emissions
4. **Extreme spikes** - > 5x historical average
5. **Source-specific checks**:
   - Flight distance > 15,000 km (impossible)
   - Energy > 1M kWh/month (huge industrial facility)

Flagged records get `status = SUSPICIOUS` and are highlighted in the analyst dashboard for manual review before approval.

## Data Flow Example

**Scenario**: Company uploads SAP fuel data

```
1. Upload SAP CSV:
   MANDT,WERKS,MENGE,MEINS,BUDAT
   100,1000,2500,L,2024-01-15

2. Create RawDataIngest
   - company: Acme Corp
   - source_type: SAP
   - raw_payload: [full CSV text]

3. Parse & Process
   - Extract: 2500 L diesel, plant 1000, date 2024-01-15
   - Normalize: 2500 L = 2500 L (already normalized)
   - Calculate CO2e: 2500 * 2.68 = 6700 kg CO2e
   - Check anomalies: None found
   - Identify scope: SCOPE_1 (direct fuel)

4. Create EmissionRecord
   - company: Acme Corp
   - activity_type: "Plant 1000 Fuel Consumption"
   - original_value: 2500, original_unit: L
   - normalized_value: 2500, normalized_unit: L
   - calculated_co2e: 6700
   - status: PENDING
   - anomaly_notes: ""

5. Create AuditLog (CREATED action)
   - action: CREATED
   - new_state: {status: PENDING, co2e: 6700}
   - performed_by: null (system)

6. Analyst Reviews
   - Can see record in dashboard
   - Can see original SAP values for verification
   - Can approve → status = APPROVED
   - Creates new AuditLog entry
```

## Why This Design?

1. **Regulatory Compliance** - Immutable audit trail for auditors
2. **Data Quality** - Anomaly detection catches obvious errors
3. **Flexibility** - Raw data never discarded, can re-normalize if logic changes
4. **Accountability** - Every change is tracked with who/when
5. **Scalability** - Multi-tenant design supports multiple organizations
6. **Standards Alignment** - Uses IPCC/EPA factors, GHG Protocol scopes
7. **Transparency** - Original values always visible alongside calculations
