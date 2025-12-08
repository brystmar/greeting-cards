"""Defines the gift-related endpoints."""
from logging import getLogger
from datetime import date
from backend import db
from models.models import Gift
from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class GiftCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_gifts
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return all gifts from the database"""
        logger.debug("Start of GiftCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all gifts from the db, sorted by id
        try:
            gifts = Gift.query.order_by(Gift.id).all()
            logger.info("Gifts retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of GiftCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of GiftCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        # Compile these data into a list
        try:
            output = []
            for gift in gifts:
                output.append(gift.to_dict())

            logger.debug("End of GiftAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of GiftCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)


class GiftApi(Resource):
    """
    Endpoint:   /api/v1/gift
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified gift id"""
        logger.debug(f"Start of GiftAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a gift_id was provided
        try:
            gift_id = args["id"]
            logger.debug(f"Gift id={gift_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing gift id: no value was provided. {e}"
            logger.info(error_msg)
            return jsonify({"error": error_msg}, status=400)

        # Retrieve the selected record
        try:
            gift = Gift.query.get(gift_id)

            if gift:
                # Record successfully returned from the db
                logger.info(f"Found the requested gift: {gift.to_dict()}")
                logger.debug("End of GiftAPI.GET")
                return gift.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No records found for gift id={gift_id}."
                logger.debug(error_msg)
                logger.debug("End of GiftAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for gift id={gift_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of GiftAPI.GET")
            return jsonify({"error": error_msg}, status=404)

    @staticmethod
    def post() -> json:
        """Add a new gift record to the database"""
        logger.debug(f"Start of GiftAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("event_id", type=int)
        parser.add_argument("household_id", type=int)
        parser.add_argument("description", type=str)
        parser.add_argument("type", type=str)
        parser.add_argument("origin", type=str)
        parser.add_argument("date", type=date)
        parser.add_argument("should_a_card_be_sent", type=str)
        parser.add_argument("notes", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Gift record using the provided data
        try:
            logger.debug(f"Attempting to create a Gift from the args.")
            new_gift = Gift(**args.__str__())
            logger.info(f"New record successfully created: {new_gift.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the gift id to the requester
            logger.debug("End of GiftAPI.POST")
            return new_gift.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Gift record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of GiftAPI.POST")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def put() -> json:
        """Update an existing record by gift id"""
        logger.debug(f"Start of GiftAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("event_id", type=int)
        parser.add_argument("household_id", type=int)
        parser.add_argument("description", type=str)
        parser.add_argument("type", type=str)
        parser.add_argument("origin", type=str)
        parser.add_argument("date", type=date)
        parser.add_argument("should_a_card_be_sent", type=str)
        parser.add_argument("notes", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a gift id was provided
        try:
            gift_id = args["id"]
            logger.debug(f"Gift id={gift_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing gift id: no value was provided. {e}"
            logger.info(error_msg)
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the specified gift record
            gift = Gift.query.get(gift_id)

            # Update this record with the provided data
            gift.event_id = args["event_id"]
            gift.households = args["households"]
            gift.description = args["description"]
            gift.origin = args["type"]
            gift.origin = args["origin"]
            gift.date = args["date"]
            gift.date = args["should_a_card_be_sent"]
            gift.notes = args["notes"]

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of GiftAPI.PUT")
            return gift.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Gift record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of GiftAPI.PUT")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def delete() -> json:
        """Delete the specified record by gift id"""
        logger.debug(f"Start of GiftAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a gift id was provided
        try:
            gift_id = args["id"]
            logger.debug(f"Gift id={gift_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing gift id: no value was provided. {e}"
            logger.info(error_msg)
            logger.debug(f"End of GiftAPI.DELETE")
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the selected record
            gift = Gift.query.get(gift_id)

            if gift:
                # Record successfully returned from the db
                logger.debug(f"Gift record found.  Attempting to delete it.")
                gift.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Gift record successfully deleted.")

                logger.debug("End of GiftAPI.GET")
                return gift.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No record found for gift id={gift_id}."
                logger.debug(error_msg)
                logger.debug("End of GiftAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for gift id={gift_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of GiftAPI.GET")
            return jsonify({"error": error_msg}, status=404)
