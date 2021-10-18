"""Defines the address-related endpoints."""
from logging import getLogger
from backend import db
from models.models import Address
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
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
            output = []

            for address in addresses:
                output.append(address.to_dict())

            logger.debug("End of AddressAPI.GET")
            return output, 200

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")
            return e, 500

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
            return e, 500
