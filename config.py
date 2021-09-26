"""Defines the object to configure parameters for our Flask app."""
from logging import getLogger
from os import environ
from main import is_running_locally


class Config(object):
    logger = getLogger(__name__)
    logger.debug("Start of the Config() class.")

    if is_running_locally:
        from env_tools import apply_env
        apply_env()
        logger.info("Local .env variables applied.")

    # App-related
    BOUND_PORT = 5000
    DOMAIN_URL = environ.get('DOMAIN_URL')
    WHITELISTED_ORIGIN = environ.get('WHITELISTED_ORIGIN')
    WHITELISTED_ORIGINS = environ.get('WHITELISTED_ORIGINS')
    SECRET_KEY = environ.get('SECRET_KEY') or '0mW7@LN0n32L6ntaj0d8jzsXiAW4mkPL7u5l'

    if SECRET_KEY != environ.get('SECRET_KEY'):
        logger.warning("Error loading SECRET_KEY!  Temporarily using a hard-coded key.")

    logger.debug("End of the Config() class.")
