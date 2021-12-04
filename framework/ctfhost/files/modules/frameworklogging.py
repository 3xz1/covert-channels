import logging
from logging.handlers import RotatingFileHandler
from logging import handlers
from sys import stdout
from modules import config
import os

# init logger
log = logging.getLogger()

# set debug level
if config.get_logging_level() == 'DEBUG':
    log.setLevel(logging.DEBUG)
elif config.get_logging_level() == 'ERROR':
    log.setLevel(logging.ERROR)
elif config.get_logging_level() == 'INFO':
    log.setLevel(logging.INFO)
elif config.get_logging_level() == 'WARNING':
    log.setLevel(logging.WARNING)

# set format
format = logging.Formatter('At %(asctime)s in %(filename)-15s (%(levelname)s) %(message)s')

# add file logging if filename exists
if config.get_logging_logfile_name() != '':
    file_logger = handlers.RotatingFileHandler(os.path.dirname(os.path.abspath(__file__)) + '/../' + config.get_logging_logfile_name())
    file_logger.setFormatter(format)
    log.addHandler(file_logger)
