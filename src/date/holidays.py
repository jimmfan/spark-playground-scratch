import pandas as pd
import holidays
from pandas.tseries.offsets import CustomBusinessDay

def get_business_day(date_type: str) -> pd.Timestamp:
    """
    Get the first or last business day of the current month, excluding US bank holidays.

    Parameters:
    date_type (str): Either "first_business_day" or "last_business_day".

    Returns:
    pd.Timestamp: The first or last business day of the month.
    """
    if date_type not in ["first_business_day", "last_business_day"]:
        raise ValueError("date_type must be 'first_business_day' or 'last_business_day'")
    
    us_holidays = holidays.US()
    custom_bday = CustomBusinessDay(holidays=us_holidays)
    today = pd.Timestamp.today()
    
    if date_type == "first_business_day":
        first_day = today.replace(day=1)
        first_bd = pd.date_range(start=first_day, periods=1, freq=custom_bday)[0]
    else:  # date_type == "last_business_day"
        last_day = today + pd.offsets.MonthEnd()
        last_bd = pd.date_range(end=last_day, periods=1, freq=custom_bday)[-1]
    
    return first_bd if date_type == "first_business_day" else last_bd

# Function to display the US holidays used
def display_us_holidays(year: int):
    us_holidays = holidays.US(years=year)
    for date, name in sorted(us_holidays.items()):
        print(f"{date}: {name}")

# Example usage:
print(get_business_day("first_business_day"))
print(get_business_day("last_business_day"))
