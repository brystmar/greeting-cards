from os import mkdir, path
import logging


# Create the logging directory, if necessary
logging_directory = "./logs"
if not path.exists(logging_directory):
    mkdir(logging_directory)

# Set config parameters
logging.basicConfig(filename=f"{logging_directory}/greeting-cards.log",
                    level=logging.DEBUG,
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filemode="w",
                    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")

# Initialize the root logger
logger = logging.getLogger()
logger.info(f"Initialized root logger at level: {logger.getEffectiveLevel()}")
