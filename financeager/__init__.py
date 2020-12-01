import os.path
from datetime import datetime as dt
from logging import DEBUG, WARN, Formatter, StreamHandler, getLogger, handlers

# versioning information
from pkg_resources import get_distribution

__version__ = get_distribution(__name__).version

#
# Global constants
#

# fixed date format for database
PERIOD_DATE_FORMAT = "%m-%d"

# default table name of database
DEFAULT_TABLE = "standard"

# Formatting option defaults
DEFAULT_CATEGORY_ENTRY_SORT_KEY = "value"
DEFAULT_BASE_ENTRY_SORT_KEY = "name"

# directories for application data and log file
CONFIG_DIR = os.path.expanduser("~/.config/financeager")
DATA_DIR = os.path.expanduser("~/.local/share/financeager")

CONFIG_FILEPATH = os.path.join(CONFIG_DIR, "config")
OFFLINE_FILEPATH = os.path.join(DATA_DIR, "offline.json")


def default_period_name():
    """The current year as string (format YYYY)."""
    return str(dt.today().year)


# Set up the package logger
LOGGER = getLogger(__package__)
LOGGER.setLevel(DEBUG)
_stream_handler = StreamHandler()
_stream_handler.setLevel(WARN)
LOGGER.addHandler(_stream_handler)
FORMATTER = Formatter(
    fmt='%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s')


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


def setup_log_file_handler(data_dir=DATA_DIR):
    """Create RotatingFileHandler for package logger, storing logs in
    'data_dir' (default: DATA_DIR). The directory is created if not existing.
    """
    os.makedirs(data_dir, exist_ok=True)
    file_handler = handlers.RotatingFileHandler(
        os.path.join(data_dir, "log"), maxBytes=5e6, backupCount=5)
    file_handler.setFormatter(FORMATTER)
    LOGGER.addHandler(file_handler)


def make_log_stream_handler_verbose():
    """Make handler show debug messages using more informative format."""
    _stream_handler.setLevel(DEBUG)
    _stream_handler.setFormatter(FORMATTER)
