"""Functions used multiple times across the API"""
from logging import getLogger

logger = getLogger()


def integer_validation(data, field_name="field", api_name="api"):
    if not int(data):
        logger.debug(f"Type: {type(data)}")
        logger.debug(f"Provided {field_name} is not an integer")
        logger.debug(f"End of {api_name}")
        return False
    else:
        return True
