"""
Master processor: Orchestrates all data processing steps.

Flow:
1. Parse raw file
2. Normalize each field
3. Calculate CO2e
4. Detect anomalies
5. Create EmissionRecord
6. Create AuditLog
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple

from apps.records.models import EmissionRecord
from apps.uploads.models import RawDataIngest
from apps.companies.models import Company

from utils.parsers import parse_sap_csv, parse_utility_csv, parse_travel_json
from utils.normalization import normalize_volume, normalize_energy, normalize_date, normalize_decimal
from utils.emissions import calculate_co2e_fuel, calculate_co2e_electricity, calculate_co2e_flight, identify_scope
from utils.anomalies import detect_anomalies, format_anomaly_notes
from utils.auditing import log_record_creation, log_record_flagged


def process_sap_upload(raw_ingest: RawDataIngest) -> List[Tuple[bool, EmissionRecord]]:
    """
    Process SAP CSV file and create emission records.
    
    Expected format:
    MANDT,WERKS,MENGE,MEINS,BUDAT
    01,001,100,L,2024-01-01
    01,001,200,L,2024-01-02
    
    Args:
        raw_ingest: The RawDataIngest object with raw_payload
    
    Returns:
        List of (success, record) tuples
    """
    results = []
    
    try:
        rows = parse_sap_csv(raw_ingest.raw_payload)
    except ValueError as e:
        # If parsing fails, return error
        return [(False, str(e))]
    
    for row in rows:
        try:
            # Extract fields
            plant = row.get('WERKS', 'Unknown')
            quantity = row.get('MENGE', '0')
            unit = row.get('MEINS', 'L')
            budat = row.get('BUDAT', '')
            
            # Normalize: volume to liters
            norm_value, norm_unit = normalize_volume(quantity, unit)
            
            # Assume it's fuel (diesel typical in SAP)
            co2e, desc = calculate_co2e_fuel(norm_value, 'DIESEL')
            
            # Identify scope
            scope = identify_scope('Fuel Consumption', 'SAP')
            
            # Check anomalies
            record_data = {
                'original_value': quantity,
                'original_unit': unit,
                'normalized_value': norm_value,
                'normalized_unit': norm_unit,
                'activity_type': f'Plant {plant} Fuel',
                'source_type': 'SAP'
            }
            has_anomaly, anomaly_list = detect_anomalies(record_data)
            
            # Create emission record
            emission_record = EmissionRecord.objects.create(
                company=raw_ingest.company,
                raw_data_ref=raw_ingest,
                activity_type=f'Plant {plant} Fuel Consumption',
                scope_category=scope,
                original_value=Decimal(str(quantity)),
                original_unit=unit,
                normalized_value=norm_value,
                normalized_unit=norm_unit,
                calculated_co2e=co2e,
                status='SUSPICIOUS' if has_anomaly else 'PENDING',
                anomaly_notes=format_anomaly_notes(anomaly_list) if has_anomaly else ''
            )
            
            # Audit log
            log_record_creation(emission_record)
            if has_anomaly:
                log_record_flagged(emission_record, anomaly_list)
            
            results.append((True, emission_record))
            
        except Exception as e:
            # Record individual errors but continue processing
            results.append((False, f"Error processing row {row}: {str(e)}"))
    
    return results


def process_utility_upload(raw_ingest: RawDataIngest) -> List[Tuple[bool, EmissionRecord]]:
    """
    Process Utility CSV file and create emission records.
    
    Expected format:
    MeterID,BillingStart,BillingEnd,kWh
    M001,2024-01-01,2024-01-31,5000
    
    Args:
        raw_ingest: The RawDataIngest object
    
    Returns:
        List of (success, record) tuples
    """
    results = []
    
    try:
        rows = parse_utility_csv(raw_ingest.raw_payload)
    except ValueError as e:
        return [(False, str(e))]
    
    for row in rows:
        try:
            meter_id = row.get('MeterID', 'Unknown')
            kwh = row.get('kWh', '0')
            bill_start = row.get('BillingStart', '')
            bill_end = row.get('BillingEnd', '')
            
            # Normalize energy to kWh
            norm_value, norm_unit = normalize_energy(kwh, 'kWh')
            
            # Calculate CO2e (use global average)
            co2e, desc = calculate_co2e_electricity(norm_value, 'GLOBAL')
            
            # Scope 2: Indirect from energy
            scope = 'SCOPE_2'
            
            # Check anomalies
            record_data = {
                'original_value': kwh,
                'original_unit': 'kWh',
                'normalized_value': norm_value,
                'normalized_unit': norm_unit,
                'activity_type': f'Meter {meter_id} Electricity',
                'source_type': 'UTILITY'
            }
            has_anomaly, anomaly_list = detect_anomalies(record_data)
            
            # Create record
            emission_record = EmissionRecord.objects.create(
                company=raw_ingest.company,
                raw_data_ref=raw_ingest,
                activity_type=f'Meter {meter_id} Electricity Usage',
                scope_category=scope,
                original_value=Decimal(str(kwh)),
                original_unit='kWh',
                normalized_value=norm_value,
                normalized_unit=norm_unit,
                calculated_co2e=co2e,
                status='SUSPICIOUS' if has_anomaly else 'PENDING',
                anomaly_notes=format_anomaly_notes(anomaly_list) if has_anomaly else ''
            )
            
            log_record_creation(emission_record)
            if has_anomaly:
                log_record_flagged(emission_record, anomaly_list)
            
            results.append((True, emission_record))
            
        except Exception as e:
            results.append((False, f"Error processing meter {row.get('MeterID', 'Unknown')}: {str(e)}"))
    
    return results


def process_travel_upload(raw_ingest: RawDataIngest) -> List[Tuple[bool, EmissionRecord]]:
    """
    Process Travel JSON file and create emission records.
    
    Expected format:
    [
        {"employee": "John", "from_airport": "DEL", "to_airport": "BLR", "date": "2024-01-15"},
        ...
    ]
    
    Args:
        raw_ingest: The RawDataIngest object
    
    Returns:
        List of (success, record) tuples
    """
    results = []
    
    try:
        flights = parse_travel_json(raw_ingest.raw_payload)
    except ValueError as e:
        return [(False, str(e))]
    
    for flight in flights:
        try:
            from_airport = flight.get('from_airport', '')
            to_airport = flight.get('to_airport', '')
            employee = flight.get('employee', 'Unknown')
            date_str = flight.get('date', '')
            cabin = flight.get('cabin_class', 'ECONOMY')
            
            # Calculate distance and CO2e
            co2e, desc = calculate_co2e_flight(from_airport, to_airport, cabin)
            
            # Scope 3: Travel
            scope = 'SCOPE_3'
            
            # For activity type, use distance extracted from description
            import re
            km_match = re.search(r'(\d+)km', desc)
            distance_km = km_match.group(1) if km_match else '0'
            
            # Check anomalies
            record_data = {
                'original_value': distance_km,
                'original_unit': 'km',
                'normalized_value': Decimal(distance_km),
                'normalized_unit': 'km',
                'activity_type': f'{employee} Flight {from_airport}→{to_airport}',
                'source_type': 'TRAVEL'
            }
            has_anomaly, anomaly_list = detect_anomalies(record_data)
            
            # Create record
            emission_record = EmissionRecord.objects.create(
                company=raw_ingest.company,
                raw_data_ref=raw_ingest,
                activity_type=f'{employee} Flight {from_airport}→{to_airport}',
                scope_category=scope,
                original_value=Decimal(distance_km),
                original_unit='km',
                normalized_value=Decimal(distance_km),
                normalized_unit='km',
                calculated_co2e=co2e,
                status='SUSPICIOUS' if has_anomaly else 'PENDING',
                anomaly_notes=format_anomaly_notes(anomaly_list) if has_anomaly else ''
            )
            
            log_record_creation(emission_record)
            if has_anomaly:
                log_record_flagged(emission_record, anomaly_list)
            
            results.append((True, emission_record))
            
        except Exception as e:
            results.append((False, f"Error processing flight from {flight.get('from_airport')}: {str(e)}"))
    
    return results
