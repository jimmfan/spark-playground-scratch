import pandas as pd
from pandas.tseries.offsets import BMonthEnd, BMonthBegin
import holidays

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
    today = pd.Timestamp.today()
    
    if date_type == "first_business_day":
        first_bd = today + BMonthBegin(n=0)
        while first_bd in us_holidays or first_bd.weekday() >= 5:
            first_bd += pd.DateOffset(days=1)
        return first_bd
    
    elif date_type == "last_business_day":
        last_bd = today + BMonthEnd(n=0)
        while last_bd in us_holidays or last_bd.weekday() >= 5:
            last_bd -= pd.DateOffset(days=1)
        return last_bd

# Example usage:
print(get_business_day("first_business_day"))
print(get_business_day("last_business_day"))
