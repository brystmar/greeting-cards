"""
Creates the household-related endpoints.
"""

from logging import getLogger
from main import app
from backend import db
from models.models import Household
from flask import request
from sqlalchemy.exc import SQLAlchemyError, InvalidRequestError, NoResultFound

logger = getLogger()


@app.route("/api/v1/all_households", methods=['GET'])
def api_household_all():
    """Return all households from the database"""
    logger.debug("Start of HouseholdCollectionAPI.GET")
    logger.debug(request)

    # Retrieve all households from the db, sorted by id
    try:
        households = Household.query.order_by(Household.id).all()
        logger.info(f"Successfully retrieved data for {households.__len__()} households.")

    except SQLAlchemyError as e:
        error_msg = f"SQLAlchemyError retrieving data: {e}"
        logger.info(error_msg)
        logger.debug("End of HouseholdCollectionAPI.GET")
        return {'message': 'Error', 'data': error_msg}, 500

    except BaseException as e:
        error_msg = f"BaseException retrieving data: {e}"
        logger.info(error_msg)
        logger.debug("End of HouseholdCollectionAPI.GET")
        return {'message': 'Error', 'data': error_msg}, 500

    # Compile these data into a list
    try:
        output = []
        for hh in households:
            output.append(hh.to_dict())

        logger.debug("End of HouseholdAPI.GET")
        return {'message': 'Success', 'data': output}, 200

    except BaseException as e:
        error_msg = f"Error compiling data into a list of `dict` to return: {e}"
        logger.info(error_msg)
        logger.debug("End of HouseholdCollectionAPI.GET")
        return {'message': 'Error', 'data': error_msg}, 500


@app.route("/api/v1/household", methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_household_one():
    logger.debug(f"Start of HouseholdAPI.{request.method.__str__()}")
    logger.debug(request)

    # Convert data from the request into a local dictionary
    form_data = request.get_json(force=True)
    logger.debug(f"Request json: {form_data}")

    if request.method == "GET":
        """Return data for the specified household_id"""
        # Validate that a household id was provided
        try:
            household_id = form_data.get('id')
            logger.debug(f"Household with id={household_id} was read successfully")
        except KeyError as e:
            logger.info(f"Error parsing household id: no value was provided. {e}")
            return f"Must provide a household id.", 400

        # Retrieve the selected record
        try:
            household = Household.query.get(household_id)

            if household:
                # Record successfully returned from the db
                logger.info(f"Found the requested household!")
                logger.debug(f"Household: {household.to_dict()}")
                logger.debug("End of HouseholdAPI.GET")
                return {"message": "Success", "data": household.to_dict()}, 200
            else:
                # No record with this id exists in the db
                logger.info(f"No household found with id={household_id}.")
                logger.debug("End of HouseholdAPI.GET")
                return {
                           "message": "Error",
                           "data":    f"No household found with id={household_id}."
                       }, 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No household found with id={household_id}.\n{e}"
            logger.info(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return {'message': 'Error', 'data': error_msg}, 404

    elif request.method == "POST":
        """Add a new household record to the database"""
        # Create a new Household record using the provided data
        try:
            logger.debug(f"Attempting to create a Household from the provided data.")
            new_household = Household(**form_data)
            db.session.add(new_household)
            db.session.flush()
            logger.info(f"New record flushed: {new_household.to_dict()}")
            logger.debug(f"Added new household record to the db session")

            # Commit this new record so the db generates an id
            logger.debug("Attempting to commit data")
            db.session.commit()
            logger.debug("Commit completed")
            logger.info(f"New record successfully created: {new_household.to_dict()}")

            # Return the household_id to the requester
            logger.debug("End of HouseholdAPI.POST")
            return {'message': 'Success', 'data': new_household.id}, 201

        except SQLAlchemyError as e:
            error_msg = f"Unable to create a new Household record.\n{e}"
            logger.debug(error_msg)
            logger.debug("End of HouseholdAPI.POST")
            return {"message": "Error", "data": error_msg}, 500

    # elif request.method == "PUT":
    #     """Update an existing record by household_id"""
    # Validate that a household_id was provided
    #     try:
    #         household_id = args["households"]
    #         logger.debug(f"Household_id={household_id} was read successfully")
    #     except KeyError as e:
    #         logger.info(f"Error parsing household_id: no value was provided. {e}")
    #         return {"message": "Error", "data": "Must provide a value for household_id."}, 400
    #
    #     try:
    #         # Retrieve the specified household record
    #         household = Household.query.get(household_id)
    #
    #         # Update this record with the provided data
    #         household.nickname = args["nickname"]
    #         household.surname = args["surname"]
    #         household.formal_name = args["formal_name"]
    #         household.relationship = args["relationship"]
    #         household.relationship_type = args["relationship_type"]
    #
    #         # Commit these changes to the db
    #         logger.debug("Attempting to commit db changes")
    #         db.session.commit()
    #         logger.info("Changes saved to the database")
    #
    #         logger.debug("End of HouseholdAPI.PUT")
    #         return household.id, 200
    #
    #     except SQLAlchemyError as e:
    #         error_msg = f"Unable to update Household record.\n{e}"
    #         logger.debug(error_msg)
    #         logger.debug("End of HouseholdAPI.PUT")
    #         return error_msg, 500

    elif request.method == "DELETE":
        """Delete the specified record by household_id"""
        # Validate that a household id was provided
        try:
            household_id = form_data.get('id')
            logger.debug(f"Household id={household_id} was provided.")
        except KeyError as e:
            logger.info(f"Missing household id. {e}")
            logger.debug(f"End of HouseholdAPI.DELETE")
            return {"message": "Error", "data": f"Missing household id. {e}"}, 400

        try:
            # Retrieve the selected record
            household_to_delete = Household.query.get(household_id)

            if household_to_delete:
                # Record successfully returned from the db
                logger.debug(f"Household record found.  Attempting to delete it.")
                db.session.delete(household_to_delete)

                logger.debug("About to commit this delete to the db.")
                db.session.commit()
                logger.debug("Commit completed.")
                logger.info("Household record successfully deleted.")

                logger.debug("End of HouseholdAPI.GET")
                return {
                           "message": "Success",
                           "data":    f"Successfully deleted household id: {household_id}"
                       }, 200
            else:
                # No record with this id exists in the db
                error_msg = f"No household found with id={household_id}."
                logger.debug(error_msg)
                logger.debug("End of HouseholdAPI.GET")
                return {"message": "Error", "data": error_msg}, 404

        except (InvalidRequestError, NoResultFound, AttributeError) as e:
            error_msg = f"No household found with id={household_id}.\n{e}"
            logger.debug(error_msg)
            logger.debug(f"End of HouseholdAPI.GET")
            return {"message": "Error", "data": error_msg}, 404
