"""Defines the family-related endpoints."""
from logging import getLogger
from backend import db
from models.models import Family
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class FamilyCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_families
    Methods:    GET
    """

    @staticmethod
    def get(self) -> json:
        """Return all families from the database"""
        logger.debug("Start of FamilyCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all families from the db, sorted by id
        try:
            families = Family.query.order_by(Family.id).all()
            logger.info("Families retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of FamilyCollectionAPI.GET")
            return error_msg, 500

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of FamilyCollectionAPI.GET")
            return error_msg, 500

        # Compile these data into a list
        try:
            output = []
            for family in families:
                output.append(family.to_dict())

            logger.debug("End of FamilyAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of FamilyCollectionAPI.GET")
            return error_msg, 500


class FamilyApi(Resource):
    """
    Endpoint:   /api/v1/family
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified family_id"""
        logger.debug(f"Start of FamilyAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("family_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a family_id was provided
        try:
            family_id = args["family_id"]
            logger.debug(f"Family_id={family_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing family_id: no value was provided. {e}")
            return f"Must provide a value for family_id.", 400

        # Retrieve the selected record
        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.info(f"Found the requested family: {family.to_dict()}")
                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for family_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for family_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for family_id={family_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404

    @staticmethod
    def post() -> json:
        """Add a new family record to the database"""
        logger.debug(f"Start of FamilyAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("nickname", type=str)
        parser.add_argument("surname", type=str)
        parser.add_argument("formal_name", type=str)
        parser.add_argument("relationship", type=str)
        parser.add_argument("relationship_type", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Family record using the provided data
        try:
            logger.debug(f"Attempting to create a Family from the args.")
            new_family = Family(**args.__str__())
            logger.info(f"New record successfully created: {new_family.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the address_id to the requester
            logger.debug("End of FamilyAPI.POST")
            return new_family.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Family record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of FamilyAPI.POST")
            return error_msg, 500

    @staticmethod
    def put() -> json:
        """Update an existing record by family_id"""
        logger.debug(f"Start of FamilyAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("nickname", type=str)
        parser.add_argument("surname", type=str)
        parser.add_argument("formal_name", type=str)
        parser.add_argument("relationship", type=str)
        parser.add_argument("relationship_type", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a family_id was provided
        try:
            family_id = args["family_id"]
            logger.debug(f"Family_id={family_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing family_id: no value was provided. {e}")
            return f"Must provide a value for family_id.", 400

        try:
            # Retrieve the specified family record
            family = Family.query.get(family_id)

            # Update this record with the provided data
            family.nickname = args["nickname"]
            family.surname = args["surname"]
            family.formal_name = args["formal_name"]
            family.relationship = args["relationship"]
            family.relationship_type = args["relationship_type"]

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of FamilyAPI.PUT")
            return family.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Family record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of FamilyAPI.PUT")
            return error_msg, 500

    @staticmethod
    def delete() -> json:
        """Delete the specified record by family_id"""
        logger.debug(f"Start of FamilyAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("family_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a family_id was provided
        try:
            family_id = args["family_id"]
            logger.debug(f"Family_id={family_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing family_id: no value was provided. {e}")
            logger.debug(f"End of AddressAPI.DELETE")
            return f"No value provided for family_id.", 400

        try:
            # Retrieve the selected record
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family record found.  Attempting to delete it.")
                family.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Family record successfully deleted.")

                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No record found for family_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No record found for family_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for family_id={family_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404
