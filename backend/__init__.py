"""Initialization file that creates the app and applies our config parameters."""
from logging import getLogger
from backend.config import Config
from flask import Flask

logger = getLogger(__name__)


def create_app(config_class=Config) -> Flask:
    logger.debug("Start of create_app()")

    # Create the Flask app
    app = Flask(__name__)
    logger.debug(f"Flask app {app.name} initialized!")

    # Apply the config parameters to this app
    app.config.from_object(config_class)
    logger.debug("App config applied")

    return app
