"""Initializes a global logger for this app."""
import logging
from os import mkdir, path

# initialize logging
log_dir = './logs'
if not path.exists(log_dir):
    mkdir(log_dir)

log_file = f'{log_dir}/greeting-cards.log'
log_level = logging.DEBUG

logging.basicConfig(filename=log_file,
                    level=log_level,
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='w',
                    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

logger.info(f"Global logging initialized!  Level: {logger.getEffectiveLevel()}")
