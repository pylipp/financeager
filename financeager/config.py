"""
Configuration of the financeager application.
"""
import os
import configparser


def _load():
    """
    Load configuration from file. Create directory/file if it does not exist.
    """

    filename = "config"
    path = os.path.join(CONFIG_DIR, filename)

    parser = configparser.ConfigParser(allow_no_value=True)

    if os.path.isfile(path):
        parser.read(path)
    else:
        parser["SERVICE"] = {
                "name": "none"
                }
        parser["DATABASE"] = {
                "default_category": "unspecified",
                "date_format": "%%m-%%d",
                "offline_backup": "offline"
                }
        parser["SERVICE:FLASK"] = {
                "debug": False,
                "host": "127.0.0.1",
                "timeout": 10
                }
        with open(path, "w") as f:
            parser.write(f)

    return parser

# create directory at import
CONFIG_DIR = os.path.expanduser("~/.config/financeager")
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CONFIG = _load()
