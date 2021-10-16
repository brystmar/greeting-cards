"""Defines our app using the create_app function in backend/__init__.py"""
from os import mkdir, path
from backend import create_app
from backend.config import Config
import logging


# =*=* Initialize logging =*=*
# Create the logging directory, if necessary
if not path.exists(Config.LOGGING_DIRECTORY):
    mkdir(Config.LOGGING_DIRECTORY)

# Set config parameters and initialize the logger
logging.basicConfig(filename=f"{Config.LOGGING_DIRECTORY}/greeting-cards.log",
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filemode="w",
                    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")

# Get the logger we just created
logger = logging.getLogger(__name__)
logger.info(f"Global logging initialized!  Level: {logger.getEffectiveLevel()}")


# =*=* Initialize the Flask app =*=*
app = create_app()

# Create a global variable to indicate whether this app is running on the local machine
basedir = path.abspath(path.dirname(__file__))
is_running_locally = "pycharm" in basedir.lower()

if is_running_locally:
    logger.info("App is running locally.")
else:
    logger.info("App is NOT running locally.")

if __name__ == "__main__" and is_running_locally:
    app.run(host="localhost", port=Config.BOUND_PORT, debug=True)
    logger.info(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
    print(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
