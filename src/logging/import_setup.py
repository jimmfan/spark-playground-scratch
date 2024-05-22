import os
import logging
from datetime import datetime

def setup_logging(script_name):
    """
    Set up logging configuration.

    Args:
        script_name (str): Name of the script.
    """
    # Get the current datetime in a specific format
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct the log filename using the script name and datetime
    log_filename = f"{script_name}_{current_datetime}.log"

    # Configure logging to write to the constructed log file
    logging.basicConfig(filename=log_filename, level=logging.INFO)

def get_script_name():
    """
    Get the name of the script (without the extension).

    Returns:
        str: Name of the script.
    """
    return os.path.splitext(os.path.basename(__file__))[0]

# Example usage:
if __name__ == "__main__":
    script_name = get_script_name()
    setup_logging(script_name)

    # Example logging usage
    logging.info("This is a test log message.")
