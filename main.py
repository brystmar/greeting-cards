"""Defines our app using the create_app function in backend/__init__.py"""
# Built-in modules
from os import path

# Third-party packages
from flask_restful import Api
from flask_cors import CORS

# App components
from root_logger import logger  # Initialize the logger before doing anything else
from backend import create_app
from routes.address import AddressCollectionApi, AddressApi
from routes.household import HouseholdCollectionApi, HouseholdApi

# Initialize the Flask app
app = create_app()

# Enable CORS for the app
CORS(app, resources=r'/api/*')

# Initialize the api for our app
api = Api(app)
logger.info("Initialized the API for this Flask app")

# Define the functional endpoints
api.add_resource(HouseholdApi, "/api/v1/household")
api.add_resource(HouseholdCollectionApi, "/api/v1/all_households")
api.add_resource(AddressApi, "/api/v1/address")
api.add_resource(AddressCollectionApi, "/api/v1/all_addresses")

# Define a global variable to indicate whether this app is running on the local machine
is_running_locally = "pycharm" in path.abspath(path.dirname(__file__)).lower()

if is_running_locally:
    logger.info("App is running locally.")
else:
    logger.info("App is NOT running locally.")

if __name__ == "__main__" and is_running_locally:
    from backend.config import Config

    app.run(host="localhost", port=Config.BOUND_PORT, debug=True)
    logger.info(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
    print(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
