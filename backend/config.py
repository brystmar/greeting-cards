"""Defines the object to configure parameters for our Flask app."""
from logging import getLogger
from os import environ, path

logger = getLogger()


class Config(object):
    logger.debug("Start of the Config() class.")

    # If the app is running locally, our environment variables can be applied directly
    # from the local .env file
    if "pycharm" in path.abspath(path.dirname(__file__)).lower():
        logger.debug("Applying variables from local .env file")
        from env_tools import apply_env
        apply_env()
        logger.debug("Local .env variables applied")

    # App-related variables
    APP_NAME = "greeting-cards"
    BOUND_PORT = 5000
    SECRET_KEY = environ.get("SECRET_KEY") or "wyKx4azY2YQ?R4J257fi@LkNVCBmkZgR1gwFWs!whsQ2V3YB"

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    logger.debug(f"SQLAlchemy db URI: {SQLALCHEMY_DATABASE_URI}")

    # Should SQLAlchemy send a notification to the app every time an object changes?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Log a warning if the fallback secret key was used
    if SECRET_KEY != environ.get("SECRET_KEY"):
        logger.warning("Error loading SECRET_KEY!  Temporarily using a hard-coded key.")

    logger.debug("End of the Config() class.")
