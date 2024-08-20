import inspect
import os
import logging
from datetime import datetime

def setup_logging(logname, use_dir_name=False, logs_dir='logs', log_level=logging.INFO):
    """
    Set up logging configuration.

    Args:
        script_name (str): Name of the script.
    """

    log_name = log_name if log_name else get_basename(parent_dir=use_dir_name, frame=2)

    os.makedirs(f"{logs_dir}/{log_name}", exist_ok=True)

    # Get the current datetime in a specific format
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct the log filename using the script name and datetime
    log_filename = f"{current_datetime}.log"

    # Configure logging to write to the constructed log file
    logging.basicConfig(
        filename=log_filename, level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H-%M-%S"
    )

    return logging.getLogger()



def get_basename(parent_dir=False, frame=1):
    """
    Get the name of the script (without the extension).

    Returns:
        str: Name of the script.
    """

    stack = inspect.stack
    caller = stack[frame]

    if parent_dir:
        basename = os.path.basename(os.path.dirname(caller.filename))
    else:
        basename = os.path.splitext(os.path.basename(caller.filename))[0]
    
    return basename

