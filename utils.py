from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Tuple, Any

def get_today_key() -> str:
    """Returns today's date in YYYY-MM-DD format."""
    return datetime.now().strftime("%Y-%m-%d")

def get_date_range(days: int) -> List[str]:
    """Returns a list of date strings for the last N days."""
    dates = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

def get_trigger_foods(data: Dict, threshold: int = 6) -> Dict:
    """Identify meals eaten on high-symptom days."""
    trigger_foods = {}
    for date, entry in data.items():
        if entry.get("symptom_severity", 0) >= threshold:
            trigger_foods[date] = entry.get("meals", "No meals recorded")
    return trigger_foods

def convert_to_dataframe(data: Dict) -> pd.DataFrame:
    """Convert JSON data to pandas DataFrame."""
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'date'
    return df.sort_index()

def get_csv_export(data: Dict) -> str:
    """Convert data to CSV string."""
    df = convert_to_dataframe(data)
    return df.to_csv()

def get_severity_color(severity: int) -> str:
    """Returns an emoji indicator based on severity."""
    if severity < 4:
        return "🟢"
    elif severity < 7:
        return "🟡"
    else:
        return "🔴"

def validate_entry(entry: Dict) -> Tuple[bool, str]:
    """Basic validation for a data entry."""
    if not entry.get("symptom_description"):
        return False, "Symptom description is required."
    return True, "Valid"
