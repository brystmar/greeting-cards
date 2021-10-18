"""Defines the family-related endpoints."""
from logging import getLogger
from backend import db
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
import json

logger = getLogger()


class FamilyApi(Resource):
    """Endpoint: /api/v1/family"""

    def get(self) -> json:
        """Return all families from the database"""
        logger.debug("Start of FamilyAPI.GET")
        logger.debug(f"Request: {request}.")

        try:
            # Retrieve all families from the db, sorted by id
            families = Family.query.order_by(Family.id).all()
            output = []

            for fam in families:
                output.append(fam.to_dict())

            logger.debug("End of FamilyAPI.GET")
            return output

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
