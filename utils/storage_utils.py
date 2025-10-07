import json
import os
from datetime import datetime
LAST_DATES_PATH = "last_dates.json"

def load_last_dates():
    """
    Loads last known dates from LAST_DATES_PATH.
    Returns:
        Set of datetime objects.
    """
    if os.path.exists(LAST_DATES_PATH):
        with open(LAST_DATES_PATH, "r") as f:
            return set(datetime.fromisoformat(dtstr) for dtstr in json.load(f))
    return set()

def save_current_dates(dates):
    """
    Saves current dates to LAST_DATES_PATH.
    Args:
        dates: Iterable of datetime objects.
    """
    with open(LAST_DATES_PATH, "w") as f:
        json.dump([dt.isoformat() for dt in dates], f)
