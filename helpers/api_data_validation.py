"""Functions used multiple times across the API"""
from logging import getLogger

logger = getLogger()


def ensure_request_contains_data(data, api_name="api"):
    if data:
        return True
    else:
        logger.debug("No data found in request body.")
        logger.debug(f"End of {api_name}")
        return False
