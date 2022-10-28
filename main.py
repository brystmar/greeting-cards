"""Defines our app using the create_app function in backend/__init__.py"""
# Built-in modules
from os import path

# Third-party packages
from flask_restful import Api
from flask_cors import CORS

# App components
from root_logger import logger  # Initialize the logger before doing anything else
from backend import create_app

# Initialize the Flask app
app = create_app()

# Import our routes
from routes.address import AddressCollectionApi, AddressApi
from routes.household import HouseholdCollectionApi, HouseholdApi
from routes.event import EventCollectionApi, EventApi
from routes.gift import GiftCollectionApi, GiftApi
from routes.card import CardCollectionApi, CardApi

# Enable CORS for the app
CORS(app, resources=r'/api/*')

# Initialize the API for our app
api = Api(app)
logger.info("Initialized the API for this Flask app")

# Define the functional endpoints
api.add_resource(HouseholdApi, "/api/v1/household")
api.add_resource(HouseholdCollectionApi, "/api/v1/all_households")
api.add_resource(AddressApi, "/api/v1/address")
api.add_resource(AddressCollectionApi, "/api/v1/all_addresses")
api.add_resource(EventApi, "/api/v1/event")
api.add_resource(EventCollectionApi, "/api/v1/all_events")
api.add_resource(GiftApi, "/api/v1/gift")
api.add_resource(GiftCollectionApi, "/api/v1/all_gifts")
api.add_resource(CardApi, "/api/v1/card")
api.add_resource(CardCollectionApi, "/api/v1/all_cards")
logger.debug("Added our functional endpoints to the API")

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
