"""
Normalization utilities.

Converts messy data into standardized units and formats.
"""

from decimal import Decimal
from datetime import datetime
import re


# Unit conversion factors (all to base unit)
VOLUME_CONVERSIONS = {
    # To liters
    'L': Decimal('1'),
    'liters': Decimal('1'),
    'liter': Decimal('1'),
    'ML': Decimal('0.001'),
    'ml': Decimal('0.001'),
    'milliliters': Decimal('0.001'),
    'M3': Decimal('1000'),
    'm3': Decimal('1000'),
    'cubic_meters': Decimal('1000'),
    'gallons': Decimal('3.78541'),
    'gal': Decimal('3.78541'),
}

ENERGY_CONVERSIONS = {
    # To kWh
    'kWh': Decimal('1'),
    'kwh': Decimal('1'),
    'MWh': Decimal('1000'),
    'mwh': Decimal('1000'),
    'Wh': Decimal('0.001'),
    'wh': Decimal('0.001'),
    'joules': Decimal('0.000000278'),
    'J': Decimal('0.000000278'),
}


def normalize_volume(value: str, unit: str) -> tuple[Decimal, str]:
    """
    Normalize volume to liters.
    
    Args:
        value: Numeric value as string
        unit: Original unit (e.g., 'ML', 'M3', 'gallons')
    
    Returns:
        Tuple of (normalized_value, normalized_unit)
    
    Raises:
        ValueError: If unit not recognized
    """
    try:
        numeric_value = Decimal(str(value).strip())
    except:
        raise ValueError(f"Cannot convert '{value}' to number")
    
    # Try exact match first
    unit_clean = unit.strip()
    if unit_clean in VOLUME_CONVERSIONS:
        factor = VOLUME_CONVERSIONS[unit_clean]
        return (numeric_value * factor, 'L')
    
    # Try case-insensitive
    for key, factor in VOLUME_CONVERSIONS.items():
        if key.lower() == unit_clean.lower():
            return (numeric_value * factor, 'L')
    
    raise ValueError(f"Unknown volume unit: '{unit}'. Supported: {list(VOLUME_CONVERSIONS.keys())}")


def normalize_energy(value: str, unit: str) -> tuple[Decimal, str]:
    """
    Normalize energy to kWh.
    
    Args:
        value: Numeric value as string
        unit: Original unit (e.g., 'kWh', 'MWh', 'Wh')
    
    Returns:
        Tuple of (normalized_value, normalized_unit)
    
    Raises:
        ValueError: If unit not recognized
    """
    try:
        numeric_value = Decimal(str(value).strip())
    except:
        raise ValueError(f"Cannot convert '{value}' to number")
    
    # Try exact match first
    unit_clean = unit.strip()
    if unit_clean in ENERGY_CONVERSIONS:
        factor = ENERGY_CONVERSIONS[unit_clean]
        return (numeric_value * factor, 'kWh')
    
    # Try case-insensitive
    for key, factor in ENERGY_CONVERSIONS.items():
        if key.lower() == unit_clean.lower():
            return (numeric_value * factor, 'kWh')
    
    raise ValueError(f"Unknown energy unit: '{unit}'. Supported: {list(ENERGY_CONVERSIONS.keys())}")


def normalize_date(date_str: str) -> str:
    """
    Normalize various date formats to ISO format (YYYY-MM-DD).
    
    Supports:
    - 2024-01-15 (ISO)
    - 2024/01/15 (slashes)
    - 01-01-2024 (DD-MM-YYYY)
    - 01/01/2024 (DD/MM/YYYY)
    - 20240115 (compact YYYYMMDD)
    - 01-JAN-2024 (Oracle style)
    
    Args:
        date_str: Date in various formats
    
    Returns:
        ISO formatted date string (YYYY-MM-DD)
    
    Raises:
        ValueError: If format not recognized
    """
    if not date_str:
        raise ValueError("Date string is empty")
    
    date_str = date_str.strip()
    
    # Try common formats
    formats = [
        '%Y-%m-%d',      # 2024-01-15
        '%Y/%m/%d',      # 2024/01/15
        '%d-%m-%Y',      # 15-01-2024
        '%d/%m/%Y',      # 15/01/2024
        '%Y%m%d',        # 20240115
        '%d-%b-%Y',      # 15-JAN-2024
        '%Y-%m-%d %H:%M:%S',  # With time
        '%d.%m.%Y',      # 15.01.2024 (European)
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    raise ValueError(f"Cannot parse date: '{date_str}'. Try: YYYY-MM-DD, DD-MM-YYYY, or YYYYMMDD")


def normalize_decimal(value: str, decimal_places: int = 4) -> Decimal:
    """
    Convert value to Decimal with consistent precision.
    
    Args:
        value: Value as string
        decimal_places: Precision (default 4)
    
    Returns:
        Decimal rounded to specified places
    
    Raises:
        ValueError: If cannot convert to decimal
    """
    try:
        d = Decimal(str(value).strip())
        # Round to specified decimal places
        if d % 1 != 0:
            return d.quantize(Decimal(10) ** -decimal_places)
        return d
    except:
        raise ValueError(f"Cannot convert '{value}' to decimal number")
