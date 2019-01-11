import os.path
from datetime import datetime as dt

# versioning information
__version__ = "0.12"

#
# Global constants
#

# fixed date format for database
PERIOD_DATE_FORMAT = "%m-%d"

# directory for application data
CONFIG_DIR = os.path.expanduser("~/.config/financeager")


def default_period_name():
    """The current year as string (format YYYY)."""
    return str(dt.today().year)
