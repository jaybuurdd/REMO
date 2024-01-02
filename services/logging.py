import os
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

def config_logging():
    # create logs folder if doesn't exist already
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    
    # File rotation handler config
    # 5MB per file, keep last 3 files
    rotation_handler = RotatingFileHandler('logs/app.log', maxBytes=5*1024*1024, backupCount=3)

    rotation_handler.setLevel(logging.INFO)
    rotation_handler.setFormatter(logging.Formatter(log_format))

    # setup console handler to print to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    

    # set logging instance
    logger = logging.getLogger()
    logger.addHandler(rotation_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)

    

