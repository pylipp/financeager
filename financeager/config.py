"""Configuration of the financeager application."""
import os
from configparser import ConfigParser, NoSectionError, NoOptionError

from .entries import CategoryEntry, BaseEntry
from .httprequests import _Proxy as Flask_Proxy


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
            "default_category": CategoryEntry.DEFAULT_NAME,
            "date_format": BaseEntry.DATE_FORMAT.replace("%", "%%"),
        }
        self._parser["SERVICE:FLASK"] = {
            "host": Flask_Proxy.DEFAULT_HOST,
            "timeout": Flask_Proxy.DEFAULT_TIMEOUT,
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
