"""Defines the object to configure parameters for our Flask app."""
from logging import getLogger
from os import environ, path

from helpers.helpers import scrub_password_from_database_uri

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
    HOST_ADDRESS = environ.get("HOST_ADDRESS", "localhost")
    DEBUG_ENABLED = environ.get("DEBUG_ENABLED", "False").lower() == "true"
    BOUND_PORT = int(environ.get("BACKEND_PORT", 5001))
    logger.debug(f"Backend configured for http://{HOST_ADDRESS}:{BOUND_PORT}")

    CORS_HEADERS = "Content-Type"
    WHITELISTED_ORIGINS = environ.get("WHITELISTED_ORIGINS")

    # Log a warning if the fallback secret key is used
    SECRET_KEY = environ.get("SECRET_KEY") or "wyKx4azY2YQ?R4J257fi@LkNVCBmkZgR1gwFWs!whsQ2V3YB"
    if SECRET_KEY != environ.get("SECRET_KEY"):
        logger.warning("Error loading SECRET_KEY! Temporarily using a hard-coded key.")

    # Database
    POSTGRES_DB_CONNECTION = environ.get("POSTGRES_DB_CONNECTION")
    POSTGRES_DB_CONNECTION_DEV = environ.get("POSTGRES_DB_CONNECTION_DEV")

    # Determine which database to connect to: dev or prod
    USE_PROD_DATABASE = environ.get("USE_PROD_DATABASE", "False").lower() == "true"
    if USE_PROD_DATABASE:
        SQLALCHEMY_DATABASE_URI = POSTGRES_DB_CONNECTION
        logger.debug(f"Connecting to Production database: {scrub_password_from_database_uri(SQLALCHEMY_DATABASE_URI)}")
        print("Connecting to Prod database")
    else:
        SQLALCHEMY_DATABASE_URI = POSTGRES_DB_CONNECTION_DEV
        logger.debug(f"Connecting to Development database: {scrub_password_from_database_uri(SQLALCHEMY_DATABASE_URI)}")
        print("Connecting to Dev database")

    # Should SQLAlchemy send a notification to the app every time an object changes?
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    logger.debug("End of the Config() class.")
