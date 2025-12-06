"""
Defines our app using the create_app function in backend/__init__.py
"""

# Initialize the logger ASAP
from root_logger import logger, is_running_locally

# Built-in modules
from logging import getLogger, DEBUG

# Third-party packages
from flask_restful import Api
from flask_cors import CORS

# App components
from backend import create_app

# Enable CORS logging
# getLogger('flask_cors').level = DEBUG

# Initialize the Flask app
logger.debug("About to initialize the Flask app")
app = create_app()

# Import our routes
# Must be done after the app is initialized to avoid circular dependencies
from routes.address import AddressCollectionApi, AddressApi
from routes.household import HouseholdCollectionApi, HouseholdApi
from routes.event import EventCollectionApi, EventApi
from routes.gift import GiftCollectionApi, GiftApi
from routes.card import CardCollectionApi, CardApi
from routes.picklists import PicklistValuesApi

# Since this will only ever be a locally-run app, allow CORS for all domains on all routes
# https://flask-cors.readthedocs.io/en/latest/
CORS(app)

# Initialize the API for our app
api = Api(app)
logger.info("Initialized the API for this Flask app")

# Define the functional endpoints
logger.debug("Adding our functional endpoints to the API")
api.add_resource(AddressApi, "/api/v1/address")
api.add_resource(AddressCollectionApi, "/api/v1/all_addresses")
api.add_resource(HouseholdApi, "/api/v1/household")
api.add_resource(HouseholdCollectionApi, "/api/v1/all_households")
api.add_resource(EventApi, "/api/v1/event")
api.add_resource(EventCollectionApi, "/api/v1/all_events")
api.add_resource(GiftApi, "/api/v1/gift")
api.add_resource(GiftCollectionApi, "/api/v1/all_gifts")
api.add_resource(CardApi, "/api/v1/card")
api.add_resource(CardCollectionApi, "/api/v1/all_cards")
api.add_resource(PicklistValuesApi, "/api/v1/picklist_values")
logger.debug("Functional endpoints added")

# More CORS button-mashing
# @app.after_request
# def add_header(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

from backend.config import Config
app.run(host=Config.HOST_ADDRESS, port=Config.BOUND_PORT, debug=Config.DEBUG_ENABLED)

# if __name__ == "__main__":  # and is_running_locally:
#     from backend.config import Config
#
#     app.run(host="localhost", port=Config.BOUND_PORT, debug=True)
#     logger.info(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
#     print(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
