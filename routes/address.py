"""Defines the address-related endpoints."""
from logging import getLogger
from datetime import datetime
from backend import db
from models.models import Address
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
parser = reqparse.RequestParser(trim=True)


class AddressCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_addresses
    Methods:    GET
    """

    @staticmethod
    def get(self) -> json:
        """Return all addresses from the database"""
        logger.debug("Start of AddressCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all addresses from the db, sorted by id
        try:
            addresses = Address.query.order_by(Address.id).all()
            logger.info("Addresses retrieved successfully!")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of AddressCollectionAPI.GET")
            return error_msg, 500

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of AddressCollectionAPI.GET")
            return error_msg, 500

        # Compile these data into a list
        try:
            output = []
            for address in addresses:
                output.append(address.to_dict())

            logger.debug("End of AddressCollectionAPI.GET")
            return output, 200

        except BaseException as e:
            error_msg = f"Error compiling data into a list of `dict` to return: {e}"
            logger.info(error_msg)
            logger.debug("End of AddressCollectionAPI.GET")
            return error_msg, 500


class AddressApi(Resource):
    """
    Endpoint:   /api/v1/address
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified address_id"""
        logger.debug(f"Start of AddressAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("address_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        address_id = args["address_id"]

        # Retrieve the selected record
        try:
            address = Address.query.get(address_id)

            if address:
                # Record successfully returned from the db
                logger.info(f"Address found!")
                logger.debug("End of AddressAPI.GET")
                return address.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.info(f"No records found for address_id={address_id}.")
                logger.debug("End of AddressAPI.GET")
                return f"No records found for address_id={address_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.GET")
            return error_msg, 404

    @staticmethod
    def post() -> json:
        """Add a new address to the database"""
        logger.debug(f"Start of AddressAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("family_id", type=int, nullable=False, required=True)
        parser.add_argument("line_1", type=str)
        parser.add_argument("line_2", type=str)
        parser.add_argument("city", type=str)
        parser.add_argument("state", type=str)
        parser.add_argument("zip", type=str)
        parser.add_argument("country", type=str, default="United States")
        parser.add_argument("is_current", type=int, default=1)
        parser.add_argument("is_likely_to_change", type=int, default=0)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Address record using the provided data
        try:
            logger.debug(f"Attempting to create an Address from the args.")
            new_address = Address(**args.__str__())
            logger.info(f"New record successfully created: {new_address.to_dict()}")

            # Set metadata for this new record
            new_address.date_created = datetime.utcnow()
            new_address.last_modified = new_address.date_created

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the address_id to the requester
            logger.debug("End of AddressAPI.POST")
            return new_address.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.POST")
            return error_msg, 500

    @staticmethod
    def put() -> json:
        """Update an existing record by address_id"""
        logger.debug(f"Start of AddressAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("address_id", type=int, nullable=False, store_missing=False)
        parser.add_argument("family_id", type=int, nullable=False, required=True)
        parser.add_argument("line_1", type=str)
        parser.add_argument("line_2", type=str)
        parser.add_argument("city", type=str)
        parser.add_argument("state", type=str)
        parser.add_argument("zip", type=str)
        parser.add_argument("country", type=str, default="United States")
        parser.add_argument("is_current", type=int, default=1)
        parser.add_argument("is_likely_to_change", type=int, default=0)

        # Parse the arguments provided
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        try:
            # Retrieve the specified address record
            address = Address.query.get(args["address_id"])

            # Update this record with the provided data
            address.family_id = args["family_id"]
            address.line_1 = args["line_1"]
            address.line_2 = args["line_2"]
            address.city = args["city"]
            address.state = args["state"]
            address.zip = args["zip"]
            address.country = args["country"]
            address.is_current = args["is_current"]
            address.is_likely_to_change = args["is_likely_to_change"]

            # Update last_modified to the current timestamp
            address.last_modified = datetime.utcnow()

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.info("Changes saved to the database")

            logger.debug("End of AddressAPI.PUT")
            return address.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.PUT")
            return error_msg, 500

    @staticmethod
    def delete() -> json:
        """Delete the specified record by address_id"""
        logger.debug(f"Start of AddressAPI.DELETE")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser.add_argument("address_id", type=int, nullable=False, store_missing=False,
                            required=True)

        # Parse the provided arguments
        args = parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that an address_id was provided
        try:
            address_id = args["address_id"]
            logger.debug(f"Address_id={address_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing address_id: no value was provided. {e}")
            logger.debug(f"End of AddressAPI.DELETE")
            return f"No value provided for address_id.", 400

        # Retrieve the selected record
        try:
            address = Address.query.get(address_id)

            if address:
                # Record successfully returned from the db
                logger.debug(f"Address record found.  Attempting to delete it.")
                address.delete()

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Address record successfully deleted.")

                logger.debug(f"End of AddressAPI.DELETE")
                return address.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.info(f"No record found for address_id={address_id}.")
                logger.debug(f"End of AddressAPI.DELETE")
                return f"No record found for address_id={address_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for address_id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.DELETE")
            return error_msg, 404

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemy error when attempting to delete address_id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.DELETE")
            return error_msg, 500
