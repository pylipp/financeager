"""Configuration of the financeager application."""
import os
from configparser import ConfigParser, NoSectionError, NoOptionError


class Configuration(object):
    """Wrapper around a ConfigParser object holding configuration. The default
    configuration is customizable via a config file."""

    def __init__(self, filepath=None):
        self._filepath = filepath
        self._parser = ConfigParser()
        self._init_defaults()
        self._load_custom_config()

    def _init_defaults(self):
        self._parser["SERVICE"] = {
            "name": "none",
        }
        self._parser["FRONTEND"] = {
            "default_category": "unspecified",
            "date_format": "%%m-%%d",
        }
        self._parser["SERVICE:FLASK"] = {
            "host": "127.0.0.1",
            "timeout": 10,
            "username": "",
            "password": "",
        }

    def _load_custom_config(self):
        """Update config values according to customization in config file."""
        custom_config = self._read_custom_config_from_file()
        if not custom_config:
            return

        for section in self._parser.sections():
            for item in self._parser.options(section):
                try:
                    # read raw value to avoid issues when reading date format
                    # containing percent-characters
                    custom_value = custom_config.get(section, item, raw=True)
                except (NoSectionError, NoOptionError):
                    # section or option not specified by user
                    continue
                self._parser[section][item] = custom_value

    def _read_custom_config_from_file(self):
        if self._filepath is None:
            return

        custom_config_parser = ConfigParser()
        if os.path.isfile(self._filepath):
            custom_config_parser.read(self._filepath)
        return custom_config_parser

    def __getattr__(self, name):
        """Forward unknown member names to underlying ConfigParser."""
        return getattr(self._parser, name)


# Load configuration from file. Create directory if it does not exist. This
# happens at first import of this module
CONFIG_DIR = os.path.expanduser("~/.config/financeager")
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

CONFIG_FILEPATH = os.path.join(CONFIG_DIR, "config")


def get_option(section, option):
    """Get an option of the financeager configuration."""
    _config = Configuration(filepath=CONFIG_FILEPATH)
    return _config.get(section, option)
