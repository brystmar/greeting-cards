"""Defines our app using the create_app function in backend/__init__.py"""
# Built-in modules
from os import path

# Third-party packages
from flask_restful import Api

# App components
from global_logger import logger  # Initialize the logger before doing anything else
from backend import create_app
from routes.address import AddressCollectionApi
from routes.family import FamilyCollectionApi, FamilyApi

# Initialize the Flask app
app = create_app()

# Initialize the api for our app
api = Api(app)
logger.info("Initialized the API for this Flask app")

# Define the functional endpoints
api.add_resource(AddressCollectionApi, '/api/v1/addresses')
api.add_resource(FamilyCollectionApi, '/api/v1/families')
api.add_resource(FamilyApi, '/api/v1/family/', '/api/v1/family/<address_id>')

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
