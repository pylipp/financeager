# This is an examplatory WSGI configuration file. I use it to run financeager on
# pythonanywhere.
# It is assumed that the financeager project is cloned to the home directory and
# all requirements are installed.

import sys
import os

from financeager.fflask import create_app

path = os.path.expanduser('~/financeager/financeager/fflask.py')
if path not in sys.path:
    sys.path.append(path)

# the 'application' object will be used by the WSGI server
application = create_app(
    data_dir=os.path.expanduser('~/.local/share/financeager'),
    config={"DEBUG": True})
