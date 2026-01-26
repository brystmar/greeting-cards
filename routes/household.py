"""
Creates the household-related endpoints.
"""

from logging import getLogger
from backend import db
from models.models import Household
from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
from datetime import datetime, timezone
import json

logger = getLogger()

# Initialize a parser for the request parameters
base_parser = reqparse.RequestParser(trim=True)

# `id` is required for most requests
base_parser.add_argument("id", type=int, nullable=False, store_missing=False,
                         required=True)


def add_household_fields_to_parser(provided_parser) -> reqparse:
    """Adds the remaining household fields to a given parser."""
    logger.debug("Adding household fields to the parser")
    provided_parser.add_argument("nickname", type=str)
    provided_parser.add_argument("first_names", type=str)
    provided_parser.add_argument("surname", type=str)
    provided_parser.add_argument("address_to", type=str)
    provided_parser.add_argument("formal_name", type=str)
    provided_parser.add_argument("relationship", type=str)
    provided_parser.add_argument("relationship_type", type=str)
    provided_parser.add_argument("known_from", type=str)
    provided_parser.add_argument("family_side", type=str)
    provided_parser.add_argument("kids", type=str)
    provided_parser.add_argument("pets", type=str)
    provided_parser.add_argument("should_receive_holiday_card", type=str)
    provided_parser.add_argument("is_relevant", type=str)
    provided_parser.add_argument("notes", type=str)

    logger.debug("Done adding household fields to the parser")
    return provided_parser


class HouseholdCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_households
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return all households from the database. No arguments should be provided."""
        logger.debug("Start of HouseholdCollectionAPI.GET")

        # Retrieve all households from the db, sorted by id
        try:
            # households = Household.query.order_by(Household.id).all()
            query = select(Household).order_by(Household.id.asc())
            households = db.session.execute(query).scalars().all()
            logger.info(f"Successfully retrieved data for {households.__len__()} households.")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of HouseholdCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of HouseholdCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

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
            return jsonify({"error": error_msg}, status=500)


class HouseholdApi(Resource):
    """
    Endpoint:   /api/v1/household
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """
        Returns a single Household record, based on the provided household id.

        REQUIRED ARGUMENTS
            key: id, type: int
        """
        logger.debug("Start of HouseholdAPI.GET")
        logger.debug(request)

        # No need for additional parser args since the only required arg is `id`
        # Parse the arguments provided
        args = base_parser.parse_args()

        # Validate that a household id was provided
        try:
            household_id = args["id"]
            logger.debug(f"Household with id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household id: no value was provided. {e}")
            error_msg = "Must provide a household id."
            return jsonify({"error": error_msg}, status=400)

        # Retrieve the selected record
        try:
            # household = Household.query.get(household_id)
            query = select(Household).where(Household.id == household_id)
            household = db.session.execute(query).scalar_one()

            if household:
                # Record successfully returned from the db
                logger.info(f"Found the requested household!")
                logger.debug(f"Household: {household.to_dict()}")
                logger.debug("End of HouseholdAPI.GET")
                return household.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No household found with id={household_id}."
                logger.info(error_msg)
                logger.debug("End of HouseholdAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No household found with id={household_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return jsonify({"error": error_msg}, status=404)

    @staticmethod
    def post() -> json:
        """
        Add a new household record to the database

        REQUIRED ARGUMENTS
            key: nickname, type: str

        OPTIONAL ARGUMENTS
            key: id, type: int
            key: first_names, type: str
            key: surname, type: str
            key: address_to, type: str
            key: formal_name, type: str
            key: relationship, type: str
            key: relationship_type, type: str
            key: family_side, type: str
            key: kids, type: str
            key: pets, type: str
            key: should_receive_holiday_card, type: str
            key: is_relevant, type: str
            key: notes, type: str
        """

        logger.debug("Start of HouseholdAPI.POST")
        logger.debug(request)

        # Add the other household args to our parser
        parser = add_household_fields_to_parser(base_parser)

        # Remove the `id` arg from our parser; the database will generate this
        # parser.remove_argument("id")
        logger.debug(f"parser keys: {parser.args.__str__()}")

        # Parse the arguments provided
        args = parser.parse_args()

        # Create a new Household record using the provided data
        try:
            logger.debug(f"Attempting to create a Household from the provided data.")
            new_household = Household(**args)
            db.session.add(new_household)
            db.session.flush()
            logger.info(f"New record flushed has id={new_household.id}")
            logger.debug(f"Added new household record to the db session")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")
            logger.info(f"New record successfully created: {new_household.to_dict()}")

            # Return the household_id to the requester
            logger.debug("End of HouseholdAPI.POST")
            return new_household.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Household record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of HouseholdAPI.POST")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def put() -> json:
        """
        Update an existing record using the provided household id.

        REQUIRED ARGUMENTS
            key: id, type: int
            key: first_names, type: str
            key: surname, type: str
            key: address_to, type: str
            key: formal_name, type: str
            key: relationship, type: str
            key: relationship_type, type: str
            key: family_side, type: str
            key: kids, type: str
            key: pets, type: str
            key: should_receive_holiday_card, type: int
            key: notes, type: str
        """
        logger.debug("Start of HouseholdAPI.PUT")
        logger.debug(request)

        # Add the other household fields to the expected arguments
        parser = add_household_fields_to_parser(base_parser)

        # Parse the arguments provided
        logger.debug("Attempting to parse the arguments")
        args = parser.parse_args()
        logger.debug("Arguments parsed successfully")

        # Validate that a household_id was provided
        try:
            household_id = args["id"]
            logger.debug(f"Household_id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household_id: no value was provided. {e}")
            error_msg = "Must provide a value for household_id."
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the specified household record
            # household = Household.query.get(household_id)
            query = select(Household).where(Household.id == household_id)
            household = db.session.execute(query).scalar_one()

            # Update this record with the provided data
            household.nickname = args["nickname"]
            household.first_names = args["first_names"]
            household.surname = args["surname"]
            household.address_to = args["address_to"]
            household.formal_name = args["formal_name"]
            household.relationship = args["relationship"]
            household.relationship_type = args["relationship_type"]
            household.known_from = args["known_from"]
            household.family_side = args["family_side"]
            household.kids = args["kids"]
            household.pets = args["pets"]
            household.should_receive_holiday_card = args["should_receive_holiday_card"]
            household.is_relevant = args["is_relevant"]
            household.notes = args["notes"]
            household.last_modified = datetime.now(timezone.utc)

        except SQLAlchemyError as e:
            error_msg = f"Unable to update the Household record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of HouseholdAPI.PUT")
            return jsonify({"error": error_msg}, status=500)

        try:
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
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def delete() -> json:
        """
        Deletes a single Household record, based on the provided household id.

        REQUIRED ARGUMENTS
            key: id, type: int
        """
        logger.debug("Start of HouseholdAPI.DELETE")
        logger.debug(request)

        # No need for additional parser args since the only required arg is `id`
        # Parse the arguments provided
        args = base_parser.parse_args()

        # Validate that a household id was provided
        try:
            household_id = args["id"]
            logger.debug(f"Household id={household_id} was provided.")
        except KeyError as e:
            error_msg = f"Missing household id.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of HouseholdAPI.DELETE")
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the selected record
            # household_to_delete = Household.query.get(household_id)
            query = select(Household).where(Household.id == household_id)
            household_to_delete = db.session.execute(query).scalar_one()

            if household_to_delete:
                # Record successfully returned from the db
                logger.debug(f"Household record found.  Attempting to delete it.")
                db.session.delete(household_to_delete)

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Household record successfully deleted.")

                logger.debug("End of HouseholdAPI.GET")
                return f"Successfully deleted household id: {household_id}", 200
            else:
                # No record with this id exists in the db
                error_msg = f"No household found with id={household_id}."
                logger.debug(error_msg)
                logger.debug("End of HouseholdAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No household found with id={household_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return jsonify({"error": error_msg}, status=404)
