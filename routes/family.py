"""Defines the family-related endpoints."""
from logging import getLogger
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy import select, exc
import json

logger = getLogger()


class FamilyApi(Resource):
    """Endpoint: /api/v1/family"""

    def get(self) -> json:
        """Return all families from the database"""
        logger.debug(f"Request: {request}.")

        try:
            # Retrieve all families from the db, sorted by id
            families = select(Family).order_by(Family.id)

            logger.debug("End of FamilyAPI.GET")
            return families

        except exc.SQLAlchemyError as e:
            logger.debug(f"Error retrieving data: {e}")
