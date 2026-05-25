"""
Anomaly detection for emission records.

Flags suspicious data for manual review before approval.
"""

from decimal import Decimal
from typing import List, Tuple


def check_negative_value(value: Decimal) -> Tuple[bool, str]:
    """
    Check if value is negative.
    
    Negative volumes/energy don't make sense.
    
    Returns:
        Tuple of (is_anomaly, reason)
    """
    if value < 0:
        return (True, f"Negative value: {value}")
    return (False, "")


def check_value_range(value: Decimal, min_val: Decimal = None, max_val: Decimal = None) -> Tuple[bool, str]:
    """
    Check if value is within reasonable range.
    
    Args:
        value: The value to check
        min_val: Minimum reasonable value (default: 0)
        max_val: Maximum reasonable value (context-dependent)
    
    Returns:
        Tuple of (is_anomaly, reason)
    """
    if min_val is None:
        min_val = Decimal('0')
    
    if value < min_val:
        return (True, f"Value {value} below minimum {min_val}")
    
    if max_val is not None and value > max_val:
        return (True, f"Value {value} exceeds maximum {max_val}")
    
    return (False, "")


def check_spike(current_value: Decimal, baseline: Decimal, threshold: Decimal = Decimal('5')) -> Tuple[bool, str]:
    """
    Detect unusual spikes compared to baseline.
    
    Example:
    - Baseline: 1000 L per month
    - Current: 5100 L
    - Spike: 5.1x baseline → ANOMALY
    
    Args:
        current_value: Current observation
        baseline: Expected baseline value
        threshold: How many times over baseline is suspicious (default: 5x)
    
    Returns:
        Tuple of (is_anomaly, reason)
    """
    if baseline <= 0:
        return (False, "")  # Can't detect spike without baseline
    
    ratio = current_value / baseline
    
    if ratio > threshold:
        return (True, f"Value {current_value} is {ratio:.1f}x the baseline {baseline} (threshold: {threshold}x)")
    
    return (False, "")


def detect_anomalies(
    record_data: dict,
    historical_avg: Decimal = None
) -> Tuple[bool, List[str]]:
    """
    Run all anomaly checks on a record.
    
    Args:
        record_data: Dictionary with keys like:
            - original_value: The raw value
            - original_unit: The unit (for validation)
            - normalized_value: After unit conversion
            - activity_type: What kind of activity
            - source_type: Where data came from
        historical_avg: Optional baseline for spike detection
    
    Returns:
        Tuple of (has_anomaly, list_of_reasons)
    """
    anomalies = []
    
    # Check 1: Negative value
    try:
        value = Decimal(str(record_data.get('normalized_value', 0)))
        is_neg, reason = check_negative_value(value)
        if is_neg:
            anomalies.append(reason)
    except:
        pass
    
    # Check 2: Missing required fields
    required_fields = ['normalized_value', 'normalized_unit', 'activity_type']
    for field in required_fields:
        if not record_data.get(field):
            anomalies.append(f"Missing required field: {field}")
    
    # Check 3: Unknown unit (simple heuristic)
    unit = record_data.get('normalized_unit', '')
    known_units = {'L', 'kWh', 'kg', 'km', 'M3', 'Wh', 'MWh'}
    if unit and unit not in known_units:
        anomalies.append(f"Unrecognized unit: {unit}")
    
    # Check 4: Spike detection
    if historical_avg is not None:
        try:
            value = Decimal(str(record_data.get('normalized_value', 0)))
            is_spike, reason = check_spike(value, historical_avg, threshold=Decimal('5'))
            if is_spike:
                anomalies.append(reason)
        except:
            pass
    
    # Check 5: Source-specific anomalies
    source_type = record_data.get('source_type', '')
    activity_type = record_data.get('activity_type', '')
    
    if source_type == 'TRAVEL':
        # Check for reasonable flight distance
        if 'flight' in activity_type.lower():
            try:
                distance = Decimal(str(record_data.get('normalized_value', 0)))
                if distance > Decimal('15000'):  # No commercial flight > 15000km
                    anomalies.append(f"Flight distance {distance}km exceeds maximum (~15000km)")
            except:
                pass
    
    if source_type == 'UTILITY':
        # Energy consumption should be reasonable
        try:
            kwh = Decimal(str(record_data.get('normalized_value', 0)))
            if kwh > Decimal('1000000'):  # More than 1M kWh/month is huge
                anomalies.append(f"Energy consumption {kwh}kWh seems unusually high")
        except:
            pass
    
    has_anomaly = len(anomalies) > 0
    return (has_anomaly, anomalies)


def format_anomaly_notes(anomalies: List[str]) -> str:
    """
    Format list of anomalies into readable text.
    
    Args:
        anomalies: List of anomaly reasons
    
    Returns:
        Formatted string
    
    Example:
        ["Negative value: -100", "Missing field: activity_type"]
        → "1. Negative value: -100\n2. Missing field: activity_type"
    """
    if not anomalies:
        return ""
    
    return "\n".join([f"{i+1}. {reason}" for i, reason in enumerate(anomalies)])
