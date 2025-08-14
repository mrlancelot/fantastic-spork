"""Utility functions for agents"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

# Load airline data
def load_airline_data() -> Dict[str, Any]:
    """Load airline data from JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(current_dir, 'airline_data.json')
    
    with open(data_file, 'r') as f:
        return json.load(f)

# Cache airline data
_airline_data = None

def get_airline_data() -> Dict[str, Any]:
    """Get cached airline data"""
    global _airline_data
    if _airline_data is None:
        _airline_data = load_airline_data()
    return _airline_data

async def get_airline_url(airline: str) -> str:
    """
    Get airline website URL from airline name or code.
    
    Args:
        airline: Airline name or IATA code
        
    Returns:
        URL of the airline's website or Google Flights as fallback
    """
    if not airline or airline == "Unknown":
        return "https://www.google.com/travel/flights"
    
    airline_lower = airline.lower().strip()
    data = get_airline_data()
    
    # Check if it's an airline code (alias)
    if airline_lower in data['airline_aliases']:
        airline_lower = data['airline_aliases'][airline_lower]
    
    # Search across all regions
    for region, airlines in data['airlines'].items():
        if airline_lower in airlines:
            return airlines[airline_lower]
        
        # Check partial matches
        for airline_name, url in airlines.items():
            if airline_lower in airline_name or airline_name in airline_lower:
                return url
            # Check if first word matches
            if airline_lower.split()[0] == airline_name.split()[0]:
                return url
    
    # Default to Google Flights if no match found
    return "https://www.google.com/travel/flights"

def create_google_flights_url(
    origin: str, 
    dest: str, 
    departure_date: str, 
    return_date: Optional[str] = None
) -> str:
    """
    Create a Google Flights search URL.
    
    Args:
        origin: Origin airport IATA code
        dest: Destination airport IATA code
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format
        
    Returns:
        Google Flights search URL
    """
    # Format dates
    try:
        dep_date = datetime.strptime(departure_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    except:
        dep_date = departure_date
    
    base_url = "https://www.google.com/travel/flights/search"
    
    if return_date:
        try:
            ret_date = datetime.strptime(return_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except:
            ret_date = return_date
        
        # Round trip URL
        url = f"{base_url}?q=flights+from+{origin}+to+{dest}+{dep_date}+return+{ret_date}&hl=en"
    else:
        # One way URL
        url = f"{base_url}?q=flights+from+{origin}+to+{dest}+on+{dep_date}&hl=en"
    
    return url

def parse_price(price_str: str) -> float:
    """
    Parse price string to float value.
    
    Args:
        price_str: Price string like "$1,234" or "N/A"
        
    Returns:
        Float price value or 999999 for invalid prices
    """
    if not price_str or price_str == 'N/A':
        return 999999
    
    try:
        # Remove currency symbols and commas
        clean_price = price_str.replace('$', '').replace(',', '').strip()
        return float(clean_price)
    except:
        return 999999

def parse_duration(duration_str: str) -> int:
    """
    Parse duration string to total minutes.
    
    Args:
        duration_str: Duration string like "2hr 30min" or "N/A"
        
    Returns:
        Total duration in minutes or 9999 for invalid durations
    """
    if not duration_str or duration_str == 'N/A':
        return 9999
    
    total_minutes = 0
    
    try:
        # Extract hours
        if 'hr' in duration_str:
            hr_part = duration_str.split('hr')[0].strip()
            total_minutes += int(hr_part) * 60
        
        # Extract minutes
        if 'min' in duration_str:
            min_part = duration_str.split('hr')[-1].replace('min', '').strip()
            if min_part:
                total_minutes += int(min_part)
        
        return total_minutes if total_minutes > 0 else 9999
    except:
        return 9999

def format_price(price: float) -> str:
    """
    Format price as currency string.
    
    Args:
        price: Price as float
        
    Returns:
        Formatted price string like "$1,234"
    """
    if price >= 999999:
        return "N/A"
    
    return f"${price:,.0f}"

def format_duration(minutes: int) -> str:
    """
    Format duration from minutes to readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted duration string like "2hr 30min"
    """
    if minutes >= 9999:
        return "N/A"
    
    hours = minutes // 60
    mins = minutes % 60
    
    if hours > 0 and mins > 0:
        return f"{hours}hr {mins}min"
    elif hours > 0:
        return f"{hours}hr"
    else:
        return f"{mins}min"