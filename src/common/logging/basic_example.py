import logging
import os

# Set default logging level
log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=getattr(logging, log_level))

logger = logging.getLogger(__name__)

logger.debug("This will only show if DEBUG is set")
logger.info("This will show for INFO level and below")
logger.error("This will always show, unless the level is set to CRITICAL")

# another example
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

def do_something():
    logger.debug("Doing something")
    # Some operation here
    logger.info("Done doing something")

if __name__ == "__main__":
    logger.info("Script started")
    do_something()
    logger.info("Script ended")
