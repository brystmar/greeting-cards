"""Defines the family-related endpoints."""
from logging import getLogger
from datetime import datetime
from backend import db
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
from helpers.api_data_validation import ensure_request_contains_data
import json

logger = getLogger()


class FamilyCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_families
    Methods:    GET
    """

    def get(self) -> json:
        """Return all families from the database"""
        logger.debug("Start of FamilyCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all families from the db, sorted by id
        try:
            families = Family.query.order_by(Family.id).all()

            # Compile these data into a list
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
    """
    Endpoint:   /api/v1/family
    Methods:    GET, POST, PUT, DELETE
    """

    def get(self) -> json:
        """Return data for the specified family"""
        logger.debug(f"Start of FamilyAPI.GET")
        logger.debug(request)

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(family_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(family_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of FamilyAPI.GET")
            return f"Value for address_id must be an integer. {e}", 400

        # Retrieve the selected record
        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family identified: {family.to_dict()}")
                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for address_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for address_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={family_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404

    def post(self) -> json:
        """Add a new family to the database"""
        logger.debug(f"Start of FamilyAPI.POST")
        logger.debug(request)

        # Ensure data was included in the request body
        if not ensure_request_contains_data(data=request.data, api_name="FamilyAPI.POST"):
            return "POST request must contain a body.", 400

        # Parse the request body
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data provided: {data}")

        except json.JSONDecodeError as e:
            error_msg = f"Error attempting to decode the provided JSON.\n" \
                        f"{request.data.__str__()},\n{e}"
            logger.debug(error_msg)
            return error_msg, 400

        except BaseException as e:
            error_msg = f"Unknown error attempting to decode JSON.\n{e}"
            logger.debug(error_msg)
            return error_msg, 400

        # Create a new Family record using the provided data
        try:
            logger.debug("Attempting to create a new Family record from provided data.")
            new_family = Family(**data)
            logger.debug(f"New record successfully created: {new_family.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            logger.debug("End of FamilyAPI.POST")
            return new_family.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create new Family record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of FamilyAPI.POST")
            return error_msg, 500

    def put(self) -> json:
        """Update an existing record"""
        logger.debug(f"Start of FamilyAPI.PUT")
        logger.debug(request)

        # Ensure data was included in the request body
        if not ensure_request_contains_data(data=request.data, api_name="FamilyAPI.PUT"):
            return "PUT request must contain a body.", 400

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(family_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(family_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of FamilyAPI.PUT")
            return f"Value for address_id must be an integer. {e}", 400

        # Parse the request body
        try:
            data = json.loads(request.data.decode())
            logger.debug(f"Data provided: {data}")

        except json.JSONDecodeError as e:
            error_msg = f"Error attempting to decode the provided JSON.\n" \
                        f"{request.data.__str__()},\n{e}"
            logger.debug(error_msg)
            return error_msg, 400

        except BaseException as e:
            error_msg = f"Unknown error attempting to decode JSON.\n{e}"
            logger.debug(error_msg)
            return error_msg, 400

        # Retrieve the specified family record
        try:
            family = Family.query.get(family_id)
            family.nickname = data.nickname
            family.surname = data.surname
            family.formal_name = data.formal_name
            family.relationship = data.relationship
            family.relationship_type = data.relationship_type

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.debug("Changes saved to the database")

            logger.debug("End of FamilyAPI.PUT")
            return family.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Family record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of FamilyAPI.PUT")
            return error_msg, 500

    def delete(self) -> json:
        """Delete the specified record"""
        logger.debug(f"Start of FamilyAPI.DELETE")
        logger.debug(request)

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(family_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(family_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of FamilyAPI.GET")
            return f"Value for address_id must be an integer. {e}", 400

        # Retrieve the selected record
        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family record found.  Attempting to delete it.")
                family.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")

                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for address_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for address_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={family_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404
