"""Defines the family-related endpoints."""
from datetime import datetime
from logging import getLogger
from backend import db
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
from helpers.api_data_validation import integer_validation
import json

logger = getLogger()


class FamilyCollectionApi(Resource):
    """Endpoint: /api/v1/families"""

    def get(self) -> json:
        """Return all families from the database"""
        logger.debug("Start of FamilyCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all families from the db, sorted by id
        try:
            families = Family.query.order_by(Family.id).all()
            output = []

            for fam in families:
                output.append(fam.to_dict())

            logger.debug("End of FamilyAPI.GET")
            return output, 200

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")
            logger.debug("End of FamilyAPI.GET")
            return e, 500

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
            logger.debug("End of FamilyAPI.GET")
            return e, 500


class FamilyApi(Resource):
    """Endpoint: /api/v1/family/<family_id>"""

    def get(self, family_id) -> json:
        """Return data for the specified family"""
        logger.debug(f"Start of FamilyAPI.GET for family={family_id}")
        logger.debug(request)

        # Validate that the provided family_id can be converted to an integer
        # TODO: Fix this implementation
        val = integer_validation(family_id, field_name="family_id", api_name="FamilyAPI.GET")
        if not val:
            return f"Value for family_id must be an integer.", 400

        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family identified: {family.to_dict()}")
                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No family with this id exists in the db
                logger.debug(f"No records found for family_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for family_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for family_id={family_id}."
            logger.debug(f"{error_msg}\n{e}")
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404

    def post(self) -> json:
        """Add a new family to the database"""
        logger.debug(f"Start of FamilyAPI.POST")
        logger.debug(request)

        # Ensure data was included in the request body
        if not request.data:
            logger.debug("No data found in request body.")
            logger.debug("End of FamilyAPI.POST")
            return "POST request must contain a body.", 400

        # Parse the request body
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data provided: {data}")

        except json.JSONDecodeError as e:
            error_msg = "Error attempting to decode the provided JSON."
            logger.debug(f"{error_msg},\n{request.data.__str__()},\n{e}")
            return error_msg + f"\n{request.data.__str__()}", 400

        except BaseException as e:
            error_msg = "Unknown error attempting to decode JSON."
            logger.debug(f"{error_msg}\n{e}")
            return error_msg, 400

        # Create a new Family from the provided data
        try:
            new_family = Family(**data)
            new_family.date_created = datetime.utcnow()
            new_family.last_modified = new_family.date_created

            # Commit this new record so the db generates an id
            db.session.commit()

            logger.debug("End of FamilyAPI.POST")
            return new_family.id, 200

        except SQLAlchemyError as e:
            error_msg = "Unable to create new Family record."
            logger.debug(f"{error_msg}\n{e}")
            logger.debug("End of FamilyAPI.POST")
            return f"{error_msg}\n{e}", 500

    def put(self, family_id) -> json:
        """Update an existing record"""
        logger.debug(f"Start of FamilyAPI.PUT")
        logger.debug(request)

        # TODO: Generalize this section & finish the PUT method
        # Ensure data was included in the request body
        if not request.data:
            logger.debug("No data found in request body.")
            logger.debug("End of FamilyAPI.PUT")
            return "PUT request must contain a body.", 400

        # Parse the request body
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data provided: {data}")

        except json.JSONDecodeError as e:
            error_msg = "Error attempting to decode the provided JSON."
            logger.debug(f"{error_msg},\n{request.data.__str__()},\n{e}")
            return error_msg + f"\n{request.data.__str__()}", 400

        except BaseException as e:
            error_msg = "Unknown error attempting to decode JSON."
            logger.debug(f"{error_msg}\n{e}")
            return error_msg, 400

        # Retrieve the family record to modify
        try:
            new_family = Family(**data)
            new_family.date_created = datetime.utcnow()
            new_family.last_modified = new_family.date_created

            # Commit this new record so the db generates an id
            db.session.commit()

            logger.debug("End of FamilyAPI.PUT")
            return new_family.id, 200

        except SQLAlchemyError as e:
            error_msg = "Unable to update Family record."
            logger.debug(f"{error_msg}\n{e}")
            logger.debug("End of FamilyAPI.PUT")
            return f"{error_msg}\n{e}", 500
