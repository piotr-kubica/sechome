import logging
from datetime import datetime as dt
from logging.handlers import TimedRotatingFileHandler
from random import randint
from time import sleep


# module globals
update_log_filename = None
get_log_filename = None
get_base_log_filename = None
logger = None


def handle_log_filename():
    base_log_filename = 'logs/sechome_log'
    current_log_filename = 'logs/sechome_log'

    def get_base_log_filename():
        nonlocal base_log_filename
        return base_log_filename

    def get_log_filename():
        nonlocal current_log_filename
        return current_log_filename

    def update_log_filename(filename):
        nonlocal current_log_filename
        current_log_filename = filename
        return current_log_filename

    return update_log_filename, get_log_filename, get_base_log_filename
    
def setup_logger(log_namer, base_log_filename):
    # https://stackoverflow.com/questions/30079242/python-logging-handler-not-appending-formatted-string-to-log
    # https://docs.python.org/3.6/howto/logging.html#handlers
    logger = logging.getLogger(__name__)
    # d - means rotate daily
    log_handler = TimedRotatingFileHandler(base_log_filename, when="d", interval=1, backupCount=365)
    log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %a %H:%M:%S'))
    log_handler.namer = log_namer
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger


# setup
update_log_filename, get_log_filename, get_base_log_filename = handle_log_filename()
logger = setup_logger(update_log_filename, get_log_filename())
