import os.path
from logging import DEBUG, WARN, Formatter, StreamHandler, getLogger, handlers

import appdirs

# versioning information
from pkg_resources import get_distribution

__version__ = get_distribution(__name__).version

#
# Global constants
#

# default name of database
DEFAULT_POCKET_NAME = "main"

# fixed date format for database
POCKET_DATE_FORMAT = "%Y-%m-%d"

# indicator char for unsetting field during update
UNSET_INDICATOR = "-"

# tables name of database
DEFAULT_TABLE = "standard"
RECURRENT_TABLE = "recurrent"

# Formatting option defaults
DEFAULT_CATEGORY_ENTRY_SORT_KEY = "value"
DEFAULT_BASE_ENTRY_SORT_KEY = "name"

# directories for application data and log file
CONFIG_DIR = appdirs.user_config_dir("financeager")
DATA_DIR = appdirs.user_data_dir("financeager")
LOG_DIR = appdirs.user_log_dir("financeager")

CONFIG_FILEPATH = os.path.join(CONFIG_DIR, "config")

# Set up the package logger
LOGGER = getLogger(__package__)
LOGGER.setLevel(DEBUG)
_stream_handler = StreamHandler()
_stream_handler.setLevel(WARN)
LOGGER.addHandler(_stream_handler)
FORMATTER = Formatter(fmt="%(levelname)s %(asctime)s %(name)s:%(lineno)d %(message)s")


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

    LOGGER.debug(f"Set up logger: {name}")
    return logger


def setup_log_file_handler(log_dir=LOG_DIR):
    """Create RotatingFileHandler for package logger, storing logs in
    'log_dir' (default: LOG_DIR). The directory is created if not existing.
    """
    os.makedirs(log_dir, exist_ok=True)
    file_handler = handlers.RotatingFileHandler(
        os.path.join(log_dir, "log"), maxBytes=5e6, backupCount=5
    )
    file_handler.setFormatter(FORMATTER)
    LOGGER.addHandler(file_handler)


def make_log_stream_handler_verbose():
    """Make handler show debug messages using more informative format."""
    _stream_handler.setLevel(DEBUG)
    _stream_handler.setFormatter(FORMATTER)
