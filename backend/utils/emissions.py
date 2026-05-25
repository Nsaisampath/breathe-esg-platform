"""
CO2e emissions calculation.

Converts normalized data → CO2e kg using emission factors.
"""

from decimal import Decimal
import math


# Emission factors (kg CO2e per unit)
# Source: IPCC AR5, EPA, UK Government Guidelines

FUEL_EMISSION_FACTORS = {
    'DIESEL': Decimal('2.68'),          # kg CO2e per liter
    'PETROL': Decimal('2.31'),          # kg CO2e per liter
    'NATURAL_GAS': Decimal('2.04'),     # kg CO2e per cubic meter
    'LPG': Decimal('1.53'),             # kg CO2e per liter
    'KEROSENE': Decimal('2.52'),        # kg CO2e per liter
}

ENERGY_EMISSION_FACTORS = {
    'ELECTRICITY_GLOBAL': Decimal('0.7'),      # kg CO2e per kWh (global average)
    'ELECTRICITY_INDIA': Decimal('0.82'),      # kg CO2e per kWh (India coal-heavy)
    'ELECTRICITY_EU': Decimal('0.38'),         # kg CO2e per kWh (EU, more renewables)
    'ELECTRICITY_UK': Decimal('0.19'),         # kg CO2e per kWh (UK, gas + renewables)
    'ELECTRICITY_US': Decimal('0.38'),         # kg CO2e per kWh (US average)
}

TRAVEL_EMISSION_FACTORS = {
    'FLIGHT_ECONOMY': Decimal('0.12'),         # kg CO2e per km per passenger
    'FLIGHT_BUSINESS': Decimal('0.27'),        # kg CO2e per km per passenger
    'FLIGHT_FIRST': Decimal('0.35'),           # kg CO2e per km per passenger
    'CAR_PETROL': Decimal('0.21'),             # kg CO2e per km
    'CAR_DIESEL': Decimal('0.17'),             # kg CO2e per km
    'TRAIN': Decimal('0.04'),                  # kg CO2e per km
}


# Airport coordinates (IATA code -> lat, lon)
# Used for Haversine distance calculation
AIRPORT_COORDINATES = {
    'DEL': (28.5642, 77.0992),      # Delhi
    'BLR': (13.1979, 77.7064),      # Bangalore
    'BOM': (19.0886, 72.8679),      # Mumbai
    'BLG': (19.0886, 72.8679),      # Bangalore (alternate)
    'CXB': (25.3925, 88.4467),      # Kolkata
    'MAA': (12.9891, 80.1609),      # Chennai
    'HYD': (17.3732, 78.4694),      # Hyderabad
    'JFK': (40.6413, -73.7781),     # New York
    'LHR': (51.4700, -0.4543),      # London
    'CDG': (49.0097, 2.5479),       # Paris
    'SYD': (-33.9399, 151.1755),    # Sydney
    'NRT': (35.7653, 140.3926),     # Tokyo
    'SIN': (1.3521, 103.8198),      # Singapore
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great-circle distance between two points on Earth.
    
    Uses the Haversine formula to find shortest distance.
    
    Args:
        lat1, lon1: Starting point (latitude, longitude)
        lat2, lon2: Ending point (latitude, longitude)
    
    Returns:
        Distance in kilometers
    
    Formula explanation (simplified):
    1. Convert latitudes and longitudes to radians
    2. Calculate the central angle using the formula
    3. Multiply by Earth's radius (6371 km)
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_co2e_fuel(
    normalized_value: Decimal,
    fuel_type: str,
    activity_type: str = "Fuel Consumption"
) -> tuple[Decimal, str]:
    """
    Calculate CO2e for fuel consumption.
    
    Args:
        normalized_value: Value in liters
        fuel_type: Type of fuel (DIESEL, PETROL, LPG, etc.)
        activity_type: Description of activity
    
    Returns:
        Tuple of (co2e_kg, description)
    
    Example:
        co2e, desc = calculate_co2e_fuel(Decimal('1000'), 'DIESEL')
        # Decimal('2680'), "1000L diesel consumption"
    """
    fuel_type_upper = fuel_type.upper()
    
    if fuel_type_upper not in FUEL_EMISSION_FACTORS:
        raise ValueError(f"Unknown fuel type: {fuel_type}. Supported: {list(FUEL_EMISSION_FACTORS.keys())}")
    
    factor = FUEL_EMISSION_FACTORS[fuel_type_upper]
    co2e = normalized_value * factor
    
    return (co2e, f"{normalized_value}L {fuel_type} consumption")


def calculate_co2e_electricity(
    normalized_value: Decimal,
    region: str = 'GLOBAL',
    activity_type: str = "Electricity Usage"
) -> tuple[Decimal, str]:
    """
    Calculate CO2e for electricity consumption.
    
    Args:
        normalized_value: Value in kWh
        region: Geographic region for emission factor (GLOBAL, INDIA, EU, UK, US)
        activity_type: Description
    
    Returns:
        Tuple of (co2e_kg, description)
    
    Example:
        co2e, desc = calculate_co2e_electricity(Decimal('5000'), 'INDIA')
        # Decimal('4100'), "5000 kWh electricity usage (India)"
    """
    key = f"ELECTRICITY_{region.upper()}"
    
    if key not in ENERGY_EMISSION_FACTORS:
        # Default to global
        key = "ELECTRICITY_GLOBAL"
    
    factor = ENERGY_EMISSION_FACTORS[key]
    co2e = normalized_value * factor
    
    return (co2e, f"{normalized_value}kWh electricity ({region})")


def calculate_co2e_flight(
    from_airport: str,
    to_airport: str,
    cabin_class: str = 'ECONOMY'
) -> tuple[Decimal, str]:
    """
    Calculate CO2e for flight travel.
    
    Uses Haversine formula to calculate distance from airport coordinates,
    then multiplies by cabin class emission factor.
    
    Args:
        from_airport: IATA code (e.g., 'DEL')
        to_airport: IATA code (e.g., 'BLR')
        cabin_class: ECONOMY, BUSINESS, or FIRST
    
    Returns:
        Tuple of (co2e_kg, description)
    
    Example:
        co2e, desc = calculate_co2e_flight('DEL', 'BLR', 'ECONOMY')
        # Decimal('79.2'), "Flight Delhi to Bangalore (660km, economy)"
    
    Raises:
        ValueError: If airports not in database
    """
    from_code = from_airport.upper()
    to_code = to_airport.upper()
    cabin_key = f"FLIGHT_{cabin_class.upper()}"
    
    # Check if airports exist
    if from_code not in AIRPORT_COORDINATES:
        raise ValueError(f"Airport {from_code} not in database")
    if to_code not in AIRPORT_COORDINATES:
        raise ValueError(f"Airport {to_code} not in database")
    
    if cabin_key not in TRAVEL_EMISSION_FACTORS:
        # Default to economy
        cabin_key = "FLIGHT_ECONOMY"
    
    # Calculate distance
    lat1, lon1 = AIRPORT_COORDINATES[from_code]
    lat2, lon2 = AIRPORT_COORDINATES[to_code]
    distance_km = haversine_distance(lat1, lon1, lat2, lon2)
    
    # Apply emission factor
    factor = TRAVEL_EMISSION_FACTORS[cabin_key]
    co2e = Decimal(str(distance_km)) * factor
    
    return (co2e, f"Flight {from_code}→{to_code} ({distance_km:.0f}km, {cabin_class.lower()})")


def identify_scope(activity_type: str, source_type: str) -> str:
    """
    Identify emissions scope based on activity type.
    
    Scope 1: Direct emissions (fuel combustion, fleet vehicles)
    Scope 2: Indirect from energy (electricity purchased)
    Scope 3: Other indirect (travel, supply chain)
    
    Args:
        activity_type: Type of activity
        source_type: Upload source (SAP, UTILITY, TRAVEL)
    
    Returns:
        Scope category (SCOPE_1, SCOPE_2, or SCOPE_3)
    """
    activity_lower = activity_type.lower()
    
    # Scope 1: Direct emissions
    if 'fuel' in activity_lower or 'diesel' in activity_lower or 'petrol' in activity_lower:
        return 'SCOPE_1'
    if 'natural gas' in activity_lower or 'gas' in activity_lower:
        return 'SCOPE_1'
    if 'fleet' in activity_lower or 'vehicle' in activity_lower:
        return 'SCOPE_1'
    
    # Scope 2: Indirect from energy purchases
    if source_type == 'UTILITY' or 'electricity' in activity_lower or 'kwh' in activity_lower:
        return 'SCOPE_2'
    
    # Scope 3: Other indirect
    if source_type == 'TRAVEL' or 'travel' in activity_lower or 'flight' in activity_lower:
        return 'SCOPE_3'
    
    # Default
    return 'SCOPE_3'
