import os.path
from datetime import datetime as dt

import logzero

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


LOGGER = logzero.setup_logger(
    __package__,
    logfile="/home/philipp/foo.log",
    # formatter=logzero.LogFormatter(
    #     fmt='%(levelname)s %(module)s:%(lineno)d %(message)s')
)
print(LOGGER.name)


def init_logger(name):
    """Set up module logger. Library loggers are assigned the package logger as
    parent. All default handlers are removed. Any records are propagated to the
    parent package logger.
    """
    logger = logzero.setup_logger(name)

    if logger.parent.name == "root":
        # Library logger
        logger.parent = LOGGER

    logger.handlers = []
    logger.propagate = True

    print(logger.name)
    return logger
