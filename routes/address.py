"""Defines the address-related endpoints."""
from logging import getLogger
from models.models import Address
from flask import request
from flask_restful import Resource
from sqlalchemy import select, exc
import json

logger = getLogger()


class AddressApi(Resource):
    """Endpoint: /api/v1/address"""

    def get(self) -> json:
        """Return all addresses from the database"""
        logger.debug(f"Request: {request}.")

        try:
            # Retrieve all addresses from the db, sorted by id
            addresses = select(Address).order_by(Address.id)

            logger.debug("End of AddressAPI.GET")
            return addresses

        except exc.SQLAlchemyError as e:
            logger.debug(f"Error retrieving data: {e}")
