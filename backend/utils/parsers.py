"""
CSV/JSON parsing utilities.

Converts raw file content into structured data.
"""

import csv
import json
from io import StringIO
from typing import List, Dict, Any


def parse_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV text into list of dictionaries.
    
    Example:
        csv_text = "name,age\\nJohn,30\\nJane,25"
        result = parse_csv(csv_text)
        # [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}]
    
    Args:
        csv_content: CSV text (with header row)
    
    Returns:
        List of dictionaries where keys are column names
    
    Raises:
        ValueError: If CSV is malformed
    """
    try:
        f = StringIO(csv_content.strip())
        reader = csv.DictReader(f)
        rows = list(reader)
        
        if not rows:
            raise ValueError("CSV is empty (no data rows)")
        
        return rows
    
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {str(e)}")


def parse_json(json_content: str) -> Any:
    """
    Parse JSON text into Python objects.
    
    Example:
        json_text = '[{"id": 1}, {"id": 2}]'
        result = parse_json(json_text)
        # [{'id': 1}, {'id': 2}]
    
    Args:
        json_content: JSON text
    
    Returns:
        Parsed Python object (list, dict, etc.)
    
    Raises:
        ValueError: If JSON is malformed
    """
    try:
        return json.loads(json_content.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")


def parse_sap_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse SAP ERP export CSV.
    
    Expected columns: MANDT, WERKS, MENGE, MEINS, BUDAT
    
    Example SAP format:
    MANDT,WERKS,MENGE,MEINS,BUDAT
    01,001,100,L,20240101
    01,001,50,L,20240102
    
    Args:
        csv_content: Raw SAP CSV
    
    Returns:
        List of SAP records
    """
    rows = parse_csv(csv_content)
    
    # Validate expected columns
    expected = {'MANDT', 'WERKS', 'MENGE', 'MEINS', 'BUDAT'}
    if not expected.issubset(set(rows[0].keys()) if rows else {}):
        raise ValueError(f"SAP CSV missing required columns. Expected: {expected}")
    
    return rows


def parse_utility_csv(csv_content: str) -> List[Dict[str, Any]]:
    """
    Parse utility/energy billing CSV.
    
    Expected columns: MeterID, BillingStart, BillingEnd, kWh
    
    Example:
    MeterID,BillingStart,BillingEnd,kWh
    M001,2024-01-01,2024-01-31,5000
    M002,2024-01-01,2024-01-31,3200
    
    Args:
        csv_content: Raw utility CSV
    
    Returns:
        List of meter records
    """
    rows = parse_csv(csv_content)
    
    # Validate columns
    expected = {'MeterID', 'BillingStart', 'BillingEnd', 'kWh'}
    if not expected.issubset(set(rows[0].keys()) if rows else {}):
        raise ValueError(f"Utility CSV missing required columns. Expected: {expected}")
    
    return rows


def parse_travel_json(json_content: str) -> List[Dict[str, Any]]:
    """
    Parse travel/flight data JSON.
    
    Expected format: Array of flight records
    
    Example:
    [
        {"employee": "John", "from_airport": "DEL", "to_airport": "BLR", "date": "2024-01-15"},
        {"employee": "Jane", "from_airport": "BLR", "to_airport": "BOM", "date": "2024-01-16"}
    ]
    
    Why airport codes?
    - Standard IATA codes (3-letter)
    - Can look up coordinates to calculate flight distance
    - DEL = Delhi, BLR = Bangalore, BOM = Mumbai
    
    Args:
        json_content: Raw JSON
    
    Returns:
        List of flight records
    """
    data = parse_json(json_content)
    
    if not isinstance(data, list):
        raise ValueError("Travel JSON must be an array of flight records")
    
    # Validate required fields
    required = {'from_airport', 'to_airport', 'date'}
    for record in data:
        if not required.issubset(set(record.keys())):
            raise ValueError(f"Travel record missing required fields. Expected: {required}")
    
    return data
