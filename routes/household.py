"""Defines the household-related endpoints."""
from logging import getLogger
from backend import db
from models.models import Household
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class HouseholdCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_households
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return all households from the database"""
        logger.debug("Start of HouseholdCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all households from the db, sorted by id
        try:
            households = Household.query.order_by(Household.id).all()
            logger.info("Households retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of HouseholdCollectionAPI.GET")
            return error_msg, 500

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of HouseholdCollectionAPI.GET")
            return error_msg, 500

        # Compile these data into a list
        try:
            output = []
            for hh in households:
                output.append(hh.to_dict())

            logger.debug("End of HouseholdAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of HouseholdCollectionAPI.GET")
            return error_msg, 500


class HouseholdApi(Resource):
    """
    Endpoint:   /api/v1/household
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified household_id"""
        logger.debug(f"Start of HouseholdAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("household_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a household_id was provided
        try:
            household_id = args["household_id"]
            logger.debug(f"Household_id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household_id: no value was provided. {e}")
            return f"Must provide a value for household_id.", 400

        # Retrieve the selected record
        try:
            household = Household.query.get(household_id)

            if household:
                # Record successfully returned from the db
                logger.info(f"Found the requested household: {household.to_dict()}")
                logger.debug("End of HouseholdAPI.GET")
                return household.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for household_id={household_id}.")
                logger.debug("End of HouseholdAPI.GET")
                return f"No records found for household_id={household_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for household_id={household_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return error_msg, 404

    @staticmethod
    def post() -> json:
        """Add a new household record to the database"""
        logger.debug(f"Start of HouseholdAPI.POST")
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

        # Create a new Household record using the provided data
        try:
            logger.debug(f"Attempting to create a Household from the args.")
            new_household = Household(**args.__str__())
            logger.info(f"New record successfully created: {new_household.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the household_id to the requester
            logger.debug("End of HouseholdAPI.POST")
            return new_household.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Household record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of HouseholdAPI.POST")
            return error_msg, 500

    @staticmethod
    def put() -> json:
        """Update an existing record by household_id"""
        logger.debug(f"Start of HouseholdAPI.PUT")
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

        # Validate that a household_id was provided
        try:
            household_id = args["household_id"]
            logger.debug(f"Household_id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household_id: no value was provided. {e}")
            return f"Must provide a value for household_id.", 400

        try:
            # Retrieve the specified household record
            household = Household.query.get(household_id)

            # Update this record with the provided data
            household.nickname = args["nickname"]
            household.surname = args["surname"]
            household.formal_name = args["formal_name"]
            household.relationship = args["relationship"]
            household.relationship_type = args["relationship_type"]

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of HouseholdAPI.PUT")
            return household.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Household record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of HouseholdAPI.PUT")
            return error_msg, 500

    @staticmethod
    def delete() -> json:
        """Delete the specified record by household_id"""
        logger.debug(f"Start of HouseholdAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("household_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a household_id was provided
        try:
            household_id = args["household_id"]
            logger.debug(f"Household_id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household_id: no value was provided. {e}")
            logger.debug(f"End of HouseholdAPI.DELETE")
            return f"No value provided for household_id.", 400

        try:
            # Retrieve the selected record
            household = Household.query.get(household_id)

            if household:
                # Record successfully returned from the db
                logger.debug(f"Household record found.  Attempting to delete it.")
                household.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Household record successfully deleted.")

                logger.debug("End of HouseholdAPI.GET")
                return household.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No record found for household_id={household_id}."
                logger.debug(error_msg)
                logger.debug("End of HouseholdAPI.GET")
                return error_msg, 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for household_id={household_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return error_msg, 404
