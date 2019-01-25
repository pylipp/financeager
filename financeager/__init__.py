import os.path
from datetime import datetime as dt
from logging import handlers, getLogger, StreamHandler, Formatter, DEBUG, WARN

# versioning information
__version__ = "0.16"

#
# Global constants
#

# fixed date format for database
PERIOD_DATE_FORMAT = "%m-%d"

# default table name of database
DEFAULT_TABLE = "standard"

# directory for application data
CONFIG_DIR = os.path.expanduser("~/.config/financeager")

# URL endpoints
PERIODS_TAIL = "/financeager/periods"
COPY_TAIL = PERIODS_TAIL + "/copy"

# HTTP communication defaults
DEFAULT_HOST = "127.0.0.1"
DEFAULT_TIMEOUT = 10


def default_period_name():
    """The current year as string (format YYYY)."""
    return str(dt.today().year)


LOGGER = getLogger(__package__)
LOGGER.setLevel(DEBUG)
stream_handler = StreamHandler()
stream_handler.setLevel(WARN)
LOGGER.addHandler(stream_handler)
file_handler = handlers.RotatingFileHandler(os.path.expanduser("~/foo.log"))
file_handler.setFormatter(
    Formatter(
        fmt='%(levelname)s %(asctime)s %(module)s:%(lineno)d %(message)s'))
LOGGER.addHandler(file_handler)


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
