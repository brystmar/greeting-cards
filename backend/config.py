"""Defines the object to configure parameters for our Flask app."""
from logging import getLogger
from os import environ, path

logger = getLogger()


class Config(object):
    logger.debug("Start of the Config() class.")

    # If the app is running locally, apply environment variables directly from the local .env
    if "pycharm" in path.abspath(path.dirname(__file__)).lower():
        logger.debug("Applying variables from local .env file")
        from env_tools import apply_env
        apply_env()
        logger.info("Local .env variables applied")

    # App-related variables
    APP_NAME = "greeting-cards"
    HOST_ADDRESS = environ.get("HOST_ADDRESS")
    DEBUG_ENABLED = environ.get("DEBUG_ENABLED")
    BOUND_PORT = environ.get("BACKEND_PORT")
    logger.debug("Bound port: %s", BOUND_PORT)
    CORS_HEADERS = "Content-Type"
    WHITELISTED_ORIGIN = environ.get("WHITELISTED_ORIGIN")
    WHITELISTED_ORIGINS = environ.get("WHITELISTED_ORIGINS")
    # TODO: Determine which variable is actually needed

    # Log a warning if the fallback secret key is used
    SECRET_KEY = environ.get("SECRET_KEY") or "wyKx4azY2YQ?R4J257fi@LkNVCBmkZgR1gwFWs!whsQ2V3YB"
    if SECRET_KEY != environ.get("SECRET_KEY"):
        logger.warning("Error loading SECRET_KEY! Temporarily using a hard-coded key.")

    # Database
    # SQLALCHEMY_DATABASE_URI_DEV = environ.get("SQLALCHEMY_DATABASE_URI_DEV")
    # SQLALCHEMY_DATABASE_URI_PROD = environ.get("SQLALCHEMY_DATABASE_URI_PROD")
    POSTGRES_DB_CONNECTION = environ.get("POSTGRES_DB_CONNECTION")
    POSTGRES_DB_CONNECTION_DEV = environ.get("POSTGRES_DB_CONNECTION_DEV")

    # POSTGRES_DB_USERNAME = environ.get("POSTGRES_DB_USERNAME")
    # POSTGRES_DB_PASSWORD = environ.get("POSTGRES_DB_PASSWORD")
    # POSTGRES_DB_PORT = environ.get("POSTGRES_DB_PORT")

    # Use the dev database when debug mode is enabled
    SQLALCHEMY_DATABASE_URI = POSTGRES_DB_CONNECTION_DEV
    # SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_DEV
    # SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_PROD
    logger.debug(f"SQLAlchemy db URI: {SQLALCHEMY_DATABASE_URI}")

    # Should SQLAlchemy send a notification to the app every time an object changes?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    logger.debug("End of the Config() class.")
