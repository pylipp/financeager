import os.path
from datetime import datetime as dt
from logging import getLogger, StreamHandler, DEBUG, INFO, Formatter, handlers

# versioning information
__version__ = "0.19"

#
# Global constants
#

# fixed date format for database
PERIOD_DATE_FORMAT = "%m-%d"

# default table name of database
DEFAULT_TABLE = "standard"

# directories for application data and log file
CONFIG_DIR = os.path.expanduser("~/.config/financeager")
DATA_DIR = os.path.expanduser("~/.local/share/financeager")

CONFIG_FILEPATH = os.path.join(CONFIG_DIR, "config")
OFFLINE_FILEPATH = os.path.join(DATA_DIR, "offline.json")

# URL endpoints
PERIODS_TAIL = "/periods"
COPY_TAIL = PERIODS_TAIL + "/copy"

# HTTP communication defaults
DEFAULT_HOST = "http://127.0.0.1:5000"
DEFAULT_TIMEOUT = 10


def default_period_name():
    """The current year as string (format YYYY)."""
    return str(dt.today().year)


# Set up the package logger
LOGGER = getLogger(__package__)
LOGGER.setLevel(DEBUG)
_stream_handler = StreamHandler()
_stream_handler.setLevel(INFO)
LOGGER.addHandler(_stream_handler)
FORMATTER = Formatter(
    fmt='%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s')


def init_logger(name):
    """Set up module logger. Library loggers are assigned the package logger as
    parent. Any records are propagated to the parent package logger.
    """
    logger = getLogger(name)
    logger.setLevel(DEBUG)

    if logger.parent.name == "root":
        # Library logger; probably has NullHandler
        logger.parent = LOGGER

    logger.propagate = True

    LOGGER.debug("Set up logger: {}".format(name))
    return logger


def setup_log_file_handler(log_dir=DATA_DIR):
    """Create FileHandler for package logger, storing logs in 'log_dir'
    (default: DATA_DIR).
    """
    file_handler = handlers.RotatingFileHandler(os.path.join(log_dir, "log"))
    file_handler.setFormatter(FORMATTER)
    LOGGER.addHandler(file_handler)


def make_log_stream_handler_verbose():
    """Make handler show debug messages using more informative format."""
    _stream_handler.setLevel(DEBUG)
    _stream_handler.setFormatter(FORMATTER)
