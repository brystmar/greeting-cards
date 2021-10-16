"""Defines the object to configure parameters for our Flask app."""
from logging import getLogger
from os import environ
from main import is_running_locally

logger = getLogger(__name__)


class Config(object):
    logger.debug("Start of the Config() class.")

    # If the app is running locally, our environment variables can be applied directly
    # from the local .env file
    if is_running_locally:
        logger.debug("App is running locally.  Applying variables from local .env file.")
        from env_tools import apply_env
        apply_env()
        logger.debug("Local .env variables applied")
    else:
        logger.debug("App is NOT running locally.")

    # App-related variables
    BOUND_PORT = 5000
    SECRET_KEY = environ.get('SECRET_KEY') or 'wyKx4azY2YQ?R4J257fi@LkNVCBmkZgR1gwFWs!whsQ2V3YB'
    LOGGING_DIRECTORY = "./logs"

    # Log a warning if the fallback secret key was used
    if SECRET_KEY != environ.get('SECRET_KEY'):
        logger.warning("Error loading SECRET_KEY!  Temporarily using a hard-coded key.")

    logger.debug("End of the Config() class.")
