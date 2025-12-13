"""Defines the address-related endpoints."""
from logging import getLogger
from datetime import datetime, timezone
from backend import db
from models.models import Address
from flask import request, jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()

# Initialize a parser for the request parameters
base_parser = reqparse.RequestParser(trim=True)

# `id` is required for most requests
base_parser.add_argument("id", type=int, nullable=False, required=True)

def add_address_fields_to_parser(provided_parser) -> reqparse:
    """Adds the remaining address-related fields to a given parser."""
    logger.debug("Adding address fields to the parser")
    provided_parser.add_argument("line_1", type=str)
    provided_parser.add_argument("line_2", type=str)
    provided_parser.add_argument("city", type=str)
    provided_parser.add_argument("state", type=str)
    provided_parser.add_argument("zip", type=str)
    provided_parser.add_argument("country", type=str, default="United States")
    provided_parser.add_argument("is_current", type=str)
    provided_parser.add_argument("is_likely_to_change", type=str)
    provided_parser.add_argument("notes", type=str)

    logger.debug("Done adding address fields to the parser")
    return provided_parser


class AddressCollectionApi(Resource):
    """
    Endpoint:   /api/v1/all_addresses
    Methods:    GET
    """

    @staticmethod
    # @cross_origin()
    def get() -> json:
        """Return all addresses from the database"""
        logger.debug("Start of AddressCollectionAPI.GET")
        # print("Start of AddressCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all addresses from the db, sorted by id
        try:
            query = select(Address).order_by(Address.id.asc())
            addresses = db.session.execute(query).scalars().all()
            logger.info(f"Successfully retrieved data for {addresses.__len__()} addresses.")

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemyError retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of AddressCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

        except BaseException as e:
            error_msg = f"BaseException retrieving data: {e}"
            logger.info(error_msg)
            logger.debug("End of AddressCollectionAPI.GET")
            return jsonify({"error": error_msg}, status=500)

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
            return jsonify({"error": error_msg}, status=500)


class AddressApi(Resource):
    """
    Endpoint:   /api/v1/address
    Methods:    GET, POST, PUT, DELETE
    """

    @staticmethod
    def get() -> json:
        """Return data for the specified address id"""
        logger.debug(f"Start of AddressAPI.GET")
        logger.debug(request)

        # Define the parameters used by this endpoint
        base_parser.add_argument("id", type=int, nullable=False, store_missing=False,
                                 required=True)

        # Parse the provided arguments
        args = base_parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        address_id = args["id"]

        # Retrieve the selected record
        try:
            # address = Address.query.get(address_id)
            query = select(Address).where(Address.id == address_id)
            address = db.session.execute(query).scalar_one()

            if address:
                # Record successfully returned from the db
                logger.info(f"Address found!")
                logger.debug("End of AddressAPI.GET")
                return address.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No records found for address id={address_id}."
                logger.info(error_msg)
                logger.debug("End of AddressAPI.GET")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.GET")
            return jsonify({"error": error_msg}, status=404)

    @staticmethod
    def post() -> json:
        """Add a new address to the database"""
        logger.debug(f"Start of AddressAPI.POST")
        logger.debug(request)

        # Define the parameters used by this endpoint
        base_parser.add_argument("id", type=int, nullable=False, required=True)
        base_parser.add_argument("line_1", type=str)
        base_parser.add_argument("line_2", type=str)
        base_parser.add_argument("city", type=str)
        base_parser.add_argument("state", type=str)
        base_parser.add_argument("zip", type=str)
        base_parser.add_argument("country", type=str, default="United States")
        base_parser.add_argument("is_current", type=str, default="True")
        base_parser.add_argument("is_likely_to_change", type=str, default="False")

        # Parse the arguments provided
        args = base_parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Create a new Address record using the provided data
        try:
            logger.debug(f"Attempting to create an Address from the args.")
            new_address = Address(**args.__str__())
            logger.info(f"New record successfully created: {new_address.to_dict()}")

            # Set metadata for this new record
            new_address.date_created = datetime.now(timezone.utc)
            new_address.last_modified = new_address.date_created

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            # Return the newly created id to the requester
            logger.debug("End of AddressAPI.POST")
            return new_address.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.POST")
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def put() -> json:
        """Update an existing record by address_id"""
        logger.debug(f"Start of AddressAPI.PUT")
        logger.debug(request)

        # Define the parameters used by this endpoint
        parser = add_address_fields_to_parser(base_parser)

        # Parse the arguments provided
        logger.debug("Attempting to parse the arguments")
        try:
            args = parser.parse_args()
            logger.debug(f"Args parsed successfully: {args.__str__()}")
        except BaseException as e:
            error_msg = f"Unable to parse the arguments Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.PUT")
            return jsonify({"error": error_msg}, status=400)
        except TypeError as e:
            error_msg = f"Unable to parse the arguments Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.PUT")
            return jsonify({"error": error_msg}, status=400)

        try:
            # Retrieve the specified address record
            # address = Address.query.get(args["id"])
            logger.debug(f"Attempting to query for address id={args.id}")
            query = select(Address).where(Address.id == args["id"])
            address = db.session.execute(query).scalar_one()

            # Update this record with the provided data
            address.line_1 = args["line_1"]
            address.line_2 = args["line_2"]
            address.city = args["city"]
            address.state = args["state"]
            address.zip = args["zip"]
            address.country = args["country"]
            address.is_current = args["is_current"]
            address.is_likely_to_change = args["is_likely_to_change"]
            address.notes = args["notes"]

            # Set last_modified to the current timestamp
            address.last_modified = datetime.now(timezone.utc)

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
            return jsonify({"error": error_msg}, status=500)

    @staticmethod
    def delete() -> json:
        """Delete the specified record by address id"""
        logger.debug(f"Start of AddressAPI.DELETE")
        logger.debug(request)

        # Parse the provided arguments
        args = base_parser.parse_args()
        logger.debug(f"Args parsed successfully: {args.__str__()}")

        # Validate that an address id was provided
        try:
            address_id = args["id"]
            logger.debug(f"Address id={address_id} was read successfully")
        except KeyError as e:
            error_msg = f"Error parsing `id`: no value was provided. {e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.DELETE")
            return jsonify({"error": error_msg}, status=400)

        # Retrieve the selected record
        try:
            # address = Address.query.get(address_id)
            query = select(Address).where(Address.id == address_id)
            address_to_delete = db.session.execute(query).scalar_one()

            if address_to_delete:
                # Record successfully returned from the db
                logger.debug(f"Address record found, attempting to delete it.")
                address_to_delete.delete()

                logger.debug("About to commit this DELETE to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Address record successfully deleted.")

                logger.debug(f"End of AddressAPI.DELETE")
                return address_to_delete.to_dict(), 200
            else:
                # No record with this id exists in the db
                error_msg = f"No record found for address id={address_id}."
                logger.info(error_msg)
                logger.debug(f"End of AddressAPI.DELETE")
                return jsonify({"error": error_msg}, status=404)

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No record found for address id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.DELETE")
            return jsonify({"error": error_msg}, status=404)

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemy error when attempting to delete address id={address_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of AddressAPI.DELETE")
            return jsonify({"error": error_msg}, status=500)
