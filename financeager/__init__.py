import os.path
from datetime import datetime as dt

# versioning information
__version__ = "0.14"

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
