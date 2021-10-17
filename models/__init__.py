# from logging import getLogger
# from backend import Config
# from sqlalchemy import create_engine
#
# logger = getLogger()
#
# try:
#     logger.debug("Attempting to connect to SQLite database")
#     engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True, future=True)
#     logger.debug("Database connection successful!")
# except BaseException as e:
#     logger.debug(f"Error attempting database connection: {e}")
