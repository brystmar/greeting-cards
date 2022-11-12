"""Provides the default picklist values for the front end to use in forms."""

from logging import getLogger
from models.models import Picklists
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound
import json

logger = getLogger()


class PicklistValuesApi(Resource):
    """
    Endpoint:   /api/v1/picklist_values
    Methods:    GET
    """

    @staticmethod
    def get() -> json:
        """Return the default picklist values, unless a specific version is specified"""
        logger.debug("Start of PicklistValuesApi.GET")

        # Retrieve the default picklist values from the db
        version_id = 1
        try:
            values = Picklists.query.get(version_id)
            logger.debug(f"Successfully read default picklist values for version={version_id}")
            return values.to_dict(), 200

        except (SQLAlchemyError, InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No picklist values found for version={version_id}. {e}"
            logger.info(error_msg)
            logger.debug(f"End of PicklistValuesApi.GET")
            return error_msg, 404
