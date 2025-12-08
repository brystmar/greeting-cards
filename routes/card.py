"""Defines the card-related endpoints."""
from logging import getLogger
from datetime import date, datetime, timezone
from backend import db
from models.models import Card
from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class CardCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_cards
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return all cards from the database"""
        logger.debug("Start of CardCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all cards from the db, sorted by id
        try:
            cards = Card.query.order_by(Card.id).all()
            logger.info("cards retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of CardCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of CardCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        # Compile these data into a list
        try:
            output = []
            for card in cards:
                output.append(card.to_dict())

            logger.debug("End of CardAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of CardCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)


class CardApi(Resource):
    """
    Endpoint:   /api/v1/card
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified card id"""
        logger.debug(f"Start of CardAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a card id was provided
        try:
            card_id = args["id"]
            logger.debug(f"Card id={card_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing card id: no value was provided. {e}"
            logger.info(error_msg)
            return jsonify({"error": error_msg}, status=400)

        # Retrieve the selected record
        try:
            card = Card.query.get(card_id)

            if card:
                # Record successfully returned from the db
                logger.info(f"Found the requested card: {card.to_dict()}")
                logger.debug("End of CardAPI.GET")
                return card.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No records found for card id={card_id}."
                logger.debug(error_msg)
                logger.debug("End of CardAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for card id={card_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of CardAPI.GET")
            return jsonify({"error": error_msg}, status=404)

    @staticmethod
    def post() -> json:
        """Add a new card record to the database"""
        logger.debug(f"Start of CardAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("type", type=str)
        parser.add_argument("status", type=str, default="New", required=True, nullable=False)
        parser.add_argument("event_id", type=int)
        parser.add_argument("gift_id", type=int)
        parser.add_argument("household_id", type=int)
        parser.add_argument("address_id", type=int)
        parser.add_argument("date_sent", type=date)
        parser.add_argument("notes", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Card record using the provided data
        try:
            logger.debug(f"Attempting to create a Card from the args.")
            new_card = Card(**args.__str__())
            logger.info(f"New record successfully created: {new_card.to_dict()}")

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Card record.\n{e}."
            logger.info(error_msg)
            logger.debug("End of CardAPI.POST")
            return jsonify({"error": error_msg}, status=500)

        # If the new card's status is "Sent" and no value was provided for `date_sent`, set
        # the `date_sent` attribute to today.
        try:
            if new_card.status.lower() == "sent" and not new_card.date_sent:
                new_card.date_sent = datetime.now(timezone.utc).date()

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the newly generated id
            logger.debug("End of CardAPI.POST")
            return new_card.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Card record.\n{e}"
            logger.info(error_msg)
            logger.debug("End of CardAPI.POST")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def put() -> json:
        """Update an existing record by card id"""
        logger.debug(f"Start of CardAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("type", type=str)
        parser.add_argument("status", type=str, required=True, nullable=False)
        parser.add_argument("event_id", type=int)
        parser.add_argument("gift_id", type=int)
        parser.add_argument("household_id", type=int)
        parser.add_argument("address_id", type=int)
        parser.add_argument("date_sent", type=date)
        parser.add_argument("notes", type=str)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a card id was provided
        try:
            card_id = args["id"]
            logger.debug(f"Card id={card_id} was read successfully")

        except KeyError as e:
            error_msg = f"Error parsing card id: no value was provided. {e}"
            logger.info(error_msg)
            logger.debug("End of CardAPI.PUT")
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the specified card record
            card = Card.query.get(card_id)

            # Update this record with the provided data
            card.type = args["type"]
            card.status = args["status"]
            card.event_id = args["event_id"]
            card.gift_id = args["gift_id"]
            card.households = args["households"]
            card.address_id = args["address_id"]
            card.date_sent = args["date_sent"]
            card.date_sent = args["notes"]

            # If the card's status wasn't already "Sent",
            #  and the card's status is being updated to "Sent",
            #  and no value was provided for `date_sent`
            # then set the `date_sent` attribute to today.
            if card.status.lower() != "sent" and args["status"].__str__().lower() == "sent" and not args["date_sent"]:
                card.date_sent = datetime.now(timezone.utc).date()

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of CardAPI.PUT")
            return card.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Card record.\n{e}"
            logger.info(error_msg)
            logger.debug("End of CardAPI.PUT")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def delete() -> json:
        """Delete the specified record by card id"""
        logger.debug(f"Start of CardAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that a card id was provided
        try:
            card_id = args["id"]
            logger.debug(f"Card id={card_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing card id: no value was provided. {e}"
            logger.info(error_msg)
            logger.debug(f"End of CardAPI.DELETE")
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the selected record
            card = Card.query.get(card_id)

            if card:
                # Record successfully returned from the db
                logger.debug(f"Card record found.  Attempting to delete it.")
                card.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Card record successfully deleted.")

                logger.debug("End of CardAPI.GET")
                return card.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No record found for card id={card_id}."
                logger.debug(error_msg)
                logger.debug("End of CardAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for card id={card_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of CardAPI.GET")
            return jsonify({"error": error_msg}, status=404)
