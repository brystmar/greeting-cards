"""Defines the address-related endpoints."""
from logging import getLogger
from backend import db
from models.models import Address
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
import json

logger = getLogger()


class AddressApi(Resource):
    """Endpoint: /api/v1/address"""

    def get(self) -> json:
        """Return all addresses from the database"""
        logger.debug("Start of AddressAPI.GET")
        logger.debug(f"Request: {request}.")

        try:
            # Retrieve all addresses from the db, sorted by id
            addresses = Address.query.order_by(Address.id).all()
            output = []

            for address in addresses:
                output.append(address.to_dict())

            logger.debug("End of AddressAPI.GET")
            return output

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
