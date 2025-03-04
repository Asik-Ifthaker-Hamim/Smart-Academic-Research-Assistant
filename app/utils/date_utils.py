import re
from datetime import datetime, timedelta

def extract_time_period(time_range: str) -> tuple[int, str]:
    """
    Extract numeric value and time unit (days, months, years) from time range string.
    Example: 'Last 2 months' -> (2, 'months')
    """
    pattern = r'(\d+)\s*(day|days|month|months|year|years)'
    match = re.search(pattern, time_range.lower())
    
    if not match:
        return None, None
        
    value = int(match.group(1))
    unit = match.group(2).rstrip('s')  # Remove 's' to standardize unit
    return value, unit

def calculate_start_date(value: int, unit: str) -> datetime:
    """Calculate start date based on value and unit."""
    today = datetime.now()
    
    if unit == 'day':
        return today - timedelta(days=value)
    elif unit == 'month':
        # Calculate months properly
        year = today.year
        month = today.month - value
        
        # Adjust year if months go negative
        while month <= 0:
            year -= 1
            month += 12
            
        # Handle day overflow for different month lengths
        day = min(today.day, [31,29,31,30,31,30,31,31,30,31,30,31][month-1])
        return datetime(year, month, day)
    elif unit == 'year':
        return datetime(today.year - value, today.month, today.day)
    
    return today

def extract_years_from_text(time_range: str) -> int:
    """Extracts numerical year value from a time range string (e.g., 'last 3 years')."""
    try:
        words = time_range.lower().split()
        for word in words:
            if word.isdigit():
                return int(word)
        return None
    except Exception as e:
        print(f"Error extracting years from text: {str(e)}")
        return None
