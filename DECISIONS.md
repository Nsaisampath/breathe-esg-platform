# Key Decisions and Rationale

## 1. Why SAP CSV for Procurement Data?

**Decision**: Use SAP ERP export CSV format with MANDT, WERKS, MENGE, MEINS, BUDAT fields

**Rationale**:
- **Industry standard**: SAP is the dominant ERP system for large companies
- **Real-world format**: Companies export raw data from SAP exactly like this
- **Messy but structured**: Contains realistic quirks (inconsistent units, duplicate entries)
- **Plant codes**: WERKS (plant) field enables facility-level tracking
- **Date field**: BUDAT enables time-series analysis and trend detection

**Alternative considered**: Generic "fuel consumption" CSV
- ❌ Too simplified
- ❌ Doesn't reflect actual enterprise data
- ❌ Missing facility tracking capability

**Reality check**: Accenture, Deloitte, real ESG consultants work with this exact format from SAP exports.

---

## 2. Why Utility Billing CSV Instead of Smart Meter APIs?

**Decision**: CSV with MeterID, BillingStart, BillingEnd, kWh (not real-time API)

**Rationale**:
- **MVP simplicity**: CSV upload works immediately without meter device integration
- **Real-world practice**: Most companies track utility usage through monthly invoices
- **Billing period**: BillingStart/BillingEnd enables month-on-month trending
- **Meter tracking**: MeterID allows per-facility energy consumption tracking
- **No device dependencies**: Works whether company has smart meters or not

**Why not smart meter APIs?**
- ❌ Requires device setup, authentication, real-time infrastructure
- ❌ Not every company has smart meters
- ❌ Still need monthly aggregate for regulatory reporting

**Future upgrade**: If needed, could add real-time meter APIs later without changing core model.

---

## 3. Why Travel JSON Instead of Just Flight Bookings?

**Decision**: JSON array with airport IATA codes + cabin class for distance + emissions calculation

**Rationale**:
- **Distance calculation**: IATA codes + Haversine formula = precise distance without external API
- **Cabin class matters**: Business ≈ 2x economy emissions per km (more seat space)
- **No dependency**: Don't need Google Maps or airline APIs
- **Complete dataset**: Includes employee name, date, class - mimics actual booking system export

**Why Haversine instead of calling Maps API?**
- ✅ Works without external dependency
- ✅ Fast and deterministic
- ✅ Deterministic testing (no API latency)
- ✅ Airport coordinates are public, stable data

**Why not hotel/ground transport data?**
- Simplified MVP
- Company travel is dominated by flights
- Hotel + ground can be added later

---

## 4. Why Keep Raw Data Immutable?

**Decision**: Store original uploaded file content in RawDataIngest.raw_payload, never delete

**Rationale**:
- **Regulatory requirement**: Auditors expect to see original documents
- **Reprocessing**: If calculation logic changes, can re-process from raw data
- **Debugging**: When analyst questions a number, can trace back to original upload
- **Accountability**: Can't accidentally lose audit trail if someone deletes EmissionRecords

**Cost**: Extra database storage is negligible compared to compliance value

**Example scenario**: 
- Year 1: Calculate flights with 0.12 kg CO2e/km economy
- Year 2: New research shows should be 0.13
- Solution: Re-run processor on all RawDataIngest records with new factor
- Previous approvals still documented with old factors, new version shows recalculation

---

## 5. Why Haversine for Flight Distance, Not Great Circle?

**Decision**: Use Haversine formula to calculate distance from airport coordinates

**Rationale**:
- Haversine IS the practical implementation of great circle distance
- Accounts for Earth's spherical shape
- Precision: accurate to ~0.5% for commercial flights
- No external API needed

**Airport coordinate database**: Hardcoded for MVP
- ✅ 15 major airports sufficient for demo
- Production would load from IATA database

---

## 6. Why Status = PENDING by Default?

**Decision**: New uploaded records get `status = PENDING` unless anomalies detected → `SUSPICIOUS`

**Rationale**:
- **Clear workflow**: 
  - PENDING = awaiting analyst review
  - SUSPICIOUS = anomalies flagged, needs attention
  - APPROVED = analyst reviewed, OK to use
  - REJECTED = analyst reviewed, data is bad
- **Attention mechanism**: Analyst naturally reviews SUSPICIOUS first
- **Audit trail**: Status changes are all logged with who/when/why

---

## 7. Why Scope Detection by Source Type?

**Decision**: Automatically categorize scope based on upload source + activity keywords

```
SAP → SCOPE_1 (fuel = direct)
UTILITY → SCOPE_2 (electricity = indirect energy)
TRAVEL → SCOPE_3 (flights = other indirect)
```

**Rationale**:
- **GHG Protocol alignment**: Standard framework
- **No user input needed**: Analysts don't have to categorize manually
- **Fallback logic**: If unsure, keywords help categorize correctly

**What analyst can override**: If needed, could add UI to let analysts change scope manually, but MVP assumes source type is correct indicator.

---

## 8. Why Anomaly Detection with Source-Specific Rules?

**Decision**: Different anomaly thresholds per source:
- Flights: max 15,000 km (impossible commercially)
- Energy: max 1M kWh/month (extreme industrial facility)
- Fuel: negative is always wrong

**Rationale**:
- One-size-fits-all rules miss real issues
- Source-specific rules catch realistic problems
- Example: 100,000 kWh/month is normal for a large building but 100 L of fuel in a day is suspicious

**Not rule-based with ML**: MVP uses simple rules
- ✅ Explainable (analyst understands why record flagged)
- ✅ Fast (no model training)
- ✅ Deterministic testing
- Future: could upgrade to ML anomaly detection

---

## 9. Why Regional Electricity Factors?

**Decision**: Support INDIA, EU, UK, US emission factors separately, default to GLOBAL

**Rationale**:
- **Grid composition matters**: 
  - India (0.82 kg CO2e/kWh) = coal-heavy grid
  - UK (0.19 kg CO2e/kWh) = gas + renewables
  - Difference: 4.3x!
- **Compliance requirement**: TCFD requires country-specific reporting
- **Realistic**: Real ESG software supports this

**Future expansion**: Load factor from live grid database if wanted

---

## 10. Why No User Authentication in MVP?

**Decision**: Accept company_id in request, no login required

**Rationale**:
- MVP focus: prove data processing works, not security
- Multi-tenancy by company_id is sufficient for demo
- Production version would add:
  - JWT token authentication
  - Role-based access (analyst, manager, admin)
  - Audit logging of who viewed what

**Security note**: Current state is not production-ready. For real deployment, add authentication.

---

## 11. Why JSON for Travel, CSV for Others?

**Decision**: Travel = JSON array, SAP/Utility = CSV rows

**Rationale**:
- **Travel booking systems** output JSON (programmatic APIs)
- **ERP/Utility exports** output CSV (legacy, human-readable)
- **Matches reality**: That's what actual systems produce
- **Parser flexibility**: Code handles both naturally

---

## 12. How Analyst Workflow Works

**Current Flow**:
1. Analyst uploads file (any source)
2. System automatically processes and flags anomalies
3. Analyst reviews dashboard (sees PENDING + SUSPICIOUS counts)
4. Can click into SUSPICIOUS records to understand what was flagged
5. Analyst approves or rejects (with optional notes)
6. Status updates, audit log created
7. Dashboard CO2e totals update

**Why this design?**
- ✅ Minimal clicking (auto-processing)
- ✅ Anomalies highlighted (attention to quality)
- ✅ Audit trail (regulatory requirement)
- ✅ No complex configuration

---

## Trade-offs Made

### What we chose:
- ✅ CSV/JSON uploads (simple)
- ✅ Manual approval workflow (transparent)
- ✅ Haversine distance (no dependency)
- ✅ Regional emission factors (realistic)
- ✅ Immutable raw data (compliance)

### What we didn't implement:
- ❌ Real-time meter API integration
- ❌ ML-based anomaly detection
- ❌ Hotel + ground transport tracking
- ❌ Complex approval routing workflows
- ❌ Multi-currency, multi-period normalization
- ❌ International airport coordinate database (hardcoded 15 for MVP)

These are reasonable MVP trade-offs. The design is extensible—each can be added later if needed.

---

## Appendix: Why This Matters

**Real ESG consultancy workflow** (from Accenture/Deloitte/KPMG):

1. Client provides raw data (SAP exports, utility bills, travel receipts)
2. Consultant normalizes and calculates emissions
3. Consultant flags outliers for client review
4. Client provides explanations ("That's our new factory opening")
5. Consultant approves and includes in TCFD report submission
6. Regulator audits and asks "Where's your source data?" → Consultant shows RawDataIngest

This system models that reality accurately.
