"""Defines the family-related endpoints."""
from datetime import datetime
from logging import getLogger
from backend import db
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()


class FamilyCollectionApi(Resource):
    """Endpoint: /api/v1/families"""

    def get(self) -> json:
        """Return all families from the database"""
        logger.debug("Start of FamilyCollectionAPI.GET")
        logger.debug(request)

        # Retrieve all families from the db, sorted by id
        try:
            families = Family.query.order_by(Family.id).all()
            output = []

            for fam in families:
                output.append(fam.to_dict())

            logger.debug("End of FamilyAPI.GET")
            return output, 200

        except SQLAlchemyError as e:
            logger.debug(f"SQLAlchemyError retrieving data: {e}")
            logger.debug("End of FamilyAPI.GET")
            return e, 500

        except BaseException as e:
            logger.debug(f"BaseException retrieving data: {e}")
            logger.debug("End of FamilyAPI.GET")
            return e, 500


class FamilyApi(Resource):
    """Endpoint: /api/v1/family/<family_id>"""

    def get(self, family_id) -> json:
        """Return data for the specified family"""
        logger.debug(f"Start of FamilyAPI.GET for family={family_id}")
        logger.debug(request)

        # Validate that the provided family_id can be converted to an integer
        if not int(family_id):
            logger.debug(f"Type: {type(family_id)}")
            logger.debug("Provided family_id is not an integer")
            logger.debug("End of FamilyAPI.GET")
            return f"Value for family_id must be an integer.", 400

        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family identified: {family.to_dict()}")
                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No family with this id exists in the db
                logger.debug(f"No records found for family_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for family_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for family_id={family_id}."
            logger.debug(f"{error_msg}\n{e}")
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404
