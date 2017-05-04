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

    parser = configparser.ConfigParser()

    if os.path.isfile(path):
        parser.read(path)
    else:
        parser["SERVICE"] = {
                "name": "flask"
                }
        parser["DATABASE"] = {
                "default_category": "unspecified",
                "date_format": "%%Y-%%m-%%d"
                }
        with open(path, "w") as f:
            parser.write(f)

    return parser

# create directory at import
CONFIG_DIR = os.path.expanduser("~/.config/financeager")
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CONFIG = _load()
