import logging
from functools import wraps
from utils.exceptions import ValidationException

def service_logger(func):
    """Logs entry, exit, and exceptions for service layer methods."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except ValidationException as ve:
            logger.warning(f"Validation failed in {func.__name__}: {ve}")
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper