from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_quarter_start_end(date_str, date_format='%Y-%m-%d'):
    # Parse the input date string to a date object
    date_obj = datetime.strptime(date_str, date_format).date()
    
    # Determine the quarter start month
    quarter_start_month = ((date_obj.month - 1) // 3) * 3 + 1
    
    # Calculate the start and end dates of the quarter
    quarter_start_date = date_obj.replace(month=quarter_start_month, day=1)
    quarter_end_date = (quarter_start_date + relativedelta(months=3) - relativedelta(days=1))
    
    # Return the start and end dates as strings in the specified format
    return quarter_start_date.strftime(date_format), quarter_end_date.strftime(date_format)

# Example usage
start_date, end_date = get_quarter_start_end('2024-07-30')
print(f"Quarter start date: {start_date}")  # Outputs '2024-07-01'
print(f"Quarter end date: {end_date}")      # Outputs '2024-09-30'
