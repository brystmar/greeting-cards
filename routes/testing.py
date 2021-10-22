from logging import getLogger
from models.models import Family
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()


class FamilyApi(Resource):
    """
    Endpoints:
        POST                /api/v1/family/
        GET, PUT, DELETE    /api/v1/family/<address_id>
    """

    def get(self, family_id) -> json:
        """Return data for the specified family"""
        logger.debug(f"Start of FamilyAPI.GET for family={family_id}")
        logger.debug(request)

        # Validate that the provided address_id can be converted to an integer
        try:
            logger.debug(f"Provided address_id={int(family_id)} is convertible to an integer.")
        except TypeError as e:
            logger.debug(f"Provided address_id is type {type(family_id)} and cannot be "
                         f"converted to an integer.")
            logger.debug(f"End of FamilyAPI.GET")
            return f"Value for address_id must be an integer. {e}", 400

        # Retrieve the selected record
        try:
            family = Family.query.get(family_id)

            if family:
                # Record successfully returned from the db
                logger.debug(f"Family identified: {family.to_dict()}")
                logger.debug("End of FamilyAPI.GET")
                return family.to_dict(), 200
            else:
                # No record with this id exists in the db
                logger.debug(f"No records found for address_id={family_id}.")
                logger.debug("End of FamilyAPI.GET")
                return f"No records found for address_id={family_id}.", 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No records found for address_id={family_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of FamilyAPI.GET")
            return error_msg, 404
