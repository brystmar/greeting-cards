"""Initialization file that creates the app and applies our config parameters."""
from logging import getLogger, DEBUG
from backend.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = getLogger()
db = SQLAlchemy()


def create_app(config_class=Config) -> Flask:
    logger.debug("Start of create_app()")

    # Create the Flask app
    app = Flask(Config.APP_NAME)
    logger.info(f"Initialized Flask app: {app.name}")

    # Apply our config parameters to the app
    app.instance_path = 'instance'
    app.config.from_object(config_class)
    logger.debug("App config applied")

    # Attach logger to the app
    app.logger = logger
    app.logger.setLevel(DEBUG)
    app.logger.info("Initialized logger for this Flask app")

    # Initialize our database and attach it to the app
    db.init_app(app)
    logger.info(f"Initialized the database {db.__repr__()}, attached it to the Flask app.")

    return app
