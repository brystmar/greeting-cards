"""Defines the event-related endpoints."""
from logging import getLogger
from datetime import date
from backend import db
from models.models import Event
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class EventCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_events
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return all events from the database"""
        logger.debug("Start of EventCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all events from the db, sorted by id
        try:
            events = Event.query.order_by(Event.id).all()
            logger.info("Events retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of EventCollectionAPI.GET")
            return error_msg, 500

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of EventCollectionAPI.GET")
            return error_msg, 500

        # Compile these data into a list
        try:
            output = []
            for event in events:
                output.append(event.to_dict())

            logger.debug("End of EventAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of EventCollectionAPI.GET")
            return error_msg, 500


class EventApi(Resource):
    """
    Endpoint:   /api/v1/event
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified event_id"""
        logger.debug(f"Start of EventAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("event_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that an event_id was provided
        try:
            event_id = args["event_id"]
            logger.debug(f"Event_id={event_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing event_id: no value was provided. {e}")
            return f"Must provide a value for event_id.", 400

        # Retrieve the selected record
        try:
            event = Event.query.get(event_id)

            if event:
                # Record successfully returned from the db
                logger.info(f"Found the requested event: {event.to_dict()}")
                logger.debug("End of EventAPI.GET")
                return event.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for event_id={event_id}.")
                logger.debug("End of EventAPI.GET")
                return f"No records found for event_id={event_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for event_id={event_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of EventAPI.GET")
            return error_msg, 404

    @staticmethod
    def post() -> json:
        """Add a new event record to the database"""
        logger.debug(f"Start of EventAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("name", type=str)
        parser.add_argument("date", type=str)
        parser.add_argument("year", type=int)
        parser.add_argument("is_archived", type=int)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Event record using the provided data
        try:
            logger.debug(f"Attempting to create a Event from the args.")
            new_event = Event(**args.__str__())
            logger.info(f"New record successfully created: {new_event.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the event_id to the requester
            logger.debug("End of EventAPI.POST")
            return new_event.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Event record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of EventAPI.POST")
            return error_msg, 500

    @staticmethod
    def put() -> json:
        """Update an existing record by event_id"""
        logger.debug(f"Start of EventAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("name", type=str)
        parser.add_argument("date", type=date)
        parser.add_argument("year", type=int)
        parser.add_argument("is_archived", type=int)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that an event_id was provided
        try:
            event_id = args["event_id"]
            logger.debug(f"Event_id={event_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing event_id: no value was provided. {e}")
            return f"Must provide a value for event_id.", 400

        try:
            # Retrieve the specified event record
            event = Event.query.get(event_id)

            # Update this record with the provided data
            event.name = args["name"]
            event.date = args["date"]
            event.year = args["year"]
            event.is_archived = args["is_archived"]

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of EventAPI.PUT")
            return event.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Event record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of EventAPI.PUT")
            return error_msg, 500

    @staticmethod
    def delete() -> json:
        """Delete the specified record by event_id"""
        logger.debug(f"Start of EventAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("event_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that an event_id was provided
        try:
            event_id = args["event_id"]
            logger.debug(f"Event_id={event_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing event_id: no value was provided. {e}")
            logger.debug(f"End of EventAPI.DELETE")
            return f"No value provided for event_id.", 400

        try:
            # Retrieve the selected record
            event = Event.query.get(event_id)

            if event:
                # Record successfully returned from the db
                logger.debug(f"Event record found.  Attempting to delete it.")
                event.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Event record successfully deleted.")

                logger.debug("End of EventAPI.GET")
                return event.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No record found for event_id={event_id}."
                logger.debug(error_msg)
                logger.debug("End of EventAPI.GET")
                return error_msg, 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for event_id={event_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of EventAPI.GET")
            return error_msg, 404
