"""Defines our app using the create_app function in backend/__init__.py"""
# System basics
from os import mkdir, path
import logging

# Packages
from flask import redirect, request
from flask_restful import Api

# App components
from backend import create_app
from backend.config import Config
from routes.address import AddressApi
from routes.family import FamilyApi


# Initialize logging
# Create the logging directory, if necessary
if not path.exists(Config.LOGGING_DIRECTORY):
    mkdir(Config.LOGGING_DIRECTORY)

# Set config parameters and initialize the logger
logging.basicConfig(filename=f"{Config.LOGGING_DIRECTORY}/greeting-cards.log",
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filemode="w",
                    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")

# Get the logger we just created
logger = logging.getLogger(__name__)
logger.info(f"Initialized global logging at level: {logger.getEffectiveLevel()}")


# Initialize the Flask app
app = create_app()

# Initialize the api for our app
api = Api(app)
logger.info("Initialized the API for this Flask app")

# Define the functional endpoints
api.add_resource(AddressApi, '/api/v1/address')
api.add_resource(FamilyApi, '/api/v1/family')


# Define a global variable to indicate whether this app is running on the local machine
is_running_locally = "pycharm" in path.abspath(path.dirname(__file__)).lower()

if is_running_locally:
    logger.info("App is running locally.")
else:
    logger.info("App is NOT running locally.")

if __name__ == "__main__" and is_running_locally:
    app.run(host="localhost", port=Config.BOUND_PORT, debug=True)
    logger.info(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
    print(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
