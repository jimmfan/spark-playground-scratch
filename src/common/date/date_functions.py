from datetime import datetime, timedelta

def calculate_date(date_key: str) -> str:
    """
    Returns the desired date based on the date_key.

    Args:
        date_key (str): The identifier for the date logic required (e.g., "prev_month_first_date").

    Returns:
        str: The calculated date as a string.
    """
    current_date = datetime.now()

    if date_key == "prev_month_first_date":
        first_day_current_month = current_date.replace(day=1)
        last_day_prev_month = first_day_current_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        return first_day_prev_month.strftime('%Y-%m-%d')
    
    elif date_key == "prev_month_last_date":
        first_day_current_month = current_date.replace(day=1)
        last_day_prev_month = first_day_current_month - timedelta(days=1)
        return last_day_prev_month.strftime('%Y-%m-%d')
    
    elif date_key == "current_month_first_date":
        first_day_current_month = current_date.replace(day=1)
        return first_day_current_month.strftime('%Y-%m-%d')
    
    elif date_key == "current_month_last_date":
        next_month = current_date.replace(day=28) + timedelta(days=4)  # this will never fail
        last_day_current_month = next_month - timedelta(days=next_month.day)
        return last_day_current_month.strftime('%Y-%m-%d')
    
    else:
        raise ValueError(f"Unknown date identifier: {date_key}")