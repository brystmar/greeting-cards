"""Defines the address-related endpoints."""
from logging import getLogger
from datetime import datetime
from backend import db
from models.models import Address
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
from helpers.api_data_validation import ensure_request_contains_data
import json

logger = getLogger()


class AddressCollectionApi(Resource):
    """Endpoint: /api/v1/addresses"""

    def get(self) -> json:
        """Return all addresses from the database"""
        logger.debug("Start of AddressCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all addresses from the db, sorted by id
        try:
            addresses = Address.query.order_by(Address.id).all()

            # Compile these data into a list
            output = []
            for address in addresses:
                output.append(address.to_dict())

            logger.debug("End of AddressCollectionAPI.GET")
            return output, 200

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")
            logger.debug("End of AddressCollectionAPI.GET")
            return e, 500

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
            logger.debug("End of AddressCollectionAPI.GET")
            return e, 500


class AddressApi(Resource):
    """
    Endpoints:
        POST                /api/v1/address/
        GET, PUT, DELETE    /api/v1/address/<address_id>
    """

    def get(self, address_id) -> json:
        """Return data for the specified address"""
        logger.debug(f"Start of AddressAPI.GET for address={address_id}")
        logger.debug(request)

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(address_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(address_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of AddressAPI.GET")
            return f"Value for address_id must be an integer. {e}", 400

        # Retrieve the selected record
        try:
            address = Address.query.get(address_id)

            if address:
                # Record successfully returned from the db
                logger.debug(f"Address identified: {address.to_dict()}")
                logger.debug("End of AddressAPI.GET")
                return address.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for address_id={address_id}.")
                logger.debug("End of AddressAPI.GET")
                return f"No records found for address_id={address_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={address_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of AddressAPI.GET")
            return error_msg, 404

    def post(self) -> json:
        """Add a new address to the database"""
        logger.debug(f"Start of AddressAPI.POST")
        logger.debug(request)

        # Ensure data was included in the request body
        if not ensure_request_contains_data(data=request.data, api_name="AddressAPI.POST"):
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

        # Create a new Address record using the provided data
        try:
            logger.debug("Attempting to create a new Address record from provided data.")
            new_address = Address(**data)
            new_address.date_created = datetime.utcnow()
            new_address.last_modified = new_address.date_created
            logger.debug(f"New record successfully created: {new_address.to_dict()}")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")

            logger.debug("End of AddressAPI.POST")
            return new_address.id, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create new Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.POST")
            return error_msg, 500

    def put(self, address_id) -> json:
        """Update an existing record"""
        logger.debug(f"Start of AddressAPI.PUT")
        logger.debug(request)

        # Ensure data was included in the request body
        if not ensure_request_contains_data(data=request.data, api_name="AddressAPI.PUT"):
            return "PUT request must contain a body.", 400

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(address_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(address_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of AddressAPI.PUT")
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

        # Retrieve the specified address record
        try:
            address = Address.query.get(address_id)
            address.nickname = data.nickname
            address.surname = data.surname
            address.formal_name = data.formal_name
            address.relationship = data.relationship
            address.relationship_type = data.relationship_type

            # Commit these changes to the db
            logger.debug("Attempting to commit db changes")
            db.session.commit()
            logger.debug("Changes saved to the database")

            logger.debug("End of AddressAPI.PUT")
            return address.id, 200

        except SQLAlchemyError as e:
            error_msg = f"Unable to update Address record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of AddressAPI.PUT")
            return error_msg, 500

    def delete(self, address_id) -> json:
        """Delete the specified record"""
        logger.debug(f"Start of AddressAPI.DELETE for address={address_id}")
        logger.debug(request)

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(address_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(address_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of AddressAPI.GET")
            return f"Value for address_id must be an integer. {e}", 400

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

                logger.debug("End of AddressAPI.GET")
                return address.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for address_id={address_id}.")
                logger.debug("End of AddressAPI.GET")
                return f"No records found for address_id={address_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={address_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of AddressAPI.GET")
            return error_msg, 404
