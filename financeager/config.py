"""Configuration of the financeager application."""
import os
from configparser import ConfigParser, NoSectionError, NoOptionError

from .entries import CategoryEntry, BaseEntry
from .exceptions import InvalidConfigError
from . import DEFAULT_HOST, DEFAULT_TIMEOUT


class Configuration(object):
    """Wrapper around a ConfigParser object holding configuration. The default
    configuration is customizable via a config file."""

    def __init__(self, filepath=None):
        """Initialize the default configuration, overwrite with custom
        configuration from file if available, and eventually validate the loaded
        configuration.

        :raises: InvalidConfigError if validation fails
        """
        self._filepath = filepath
        self._parser = ConfigParser()
        self._init_defaults()
        self._load_custom_config()
        self._validate()

    def _init_defaults(self):
        self._parser["SERVICE"] = {
            "name": "none",
        }
        self._parser["FRONTEND"] = {
            "default_category": CategoryEntry.DEFAULT_NAME,
            "date_format": BaseEntry.DATE_FORMAT.replace("%", "%%"),
        }
        self._parser["SERVICE:FLASK"] = {
            "host": DEFAULT_HOST,
            "timeout": DEFAULT_TIMEOUT,
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

    def get_option(self, section, option=None):
        """Get an option of the configuration or a dictionary of section
        contents if no option given.
        """
        if option is None:
            return dict(self._parser.items(section))
        else:
            return self.get(section, option)

    def _validate(self):
        """Validate certain fields of the configuration.
        :raises: InvalidConfigError
        """
        if self.get_option("SERVICE", "name") not in ("flask", "none"):
            raise InvalidConfigError("Unknown service name!")

        if len(self.get_option("FRONTEND", "default_category")) < 1:
            raise InvalidConfigError("Default category name too short!")

        if len(self.get_option("SERVICE:FLASK", "host")) < 1:
            raise InvalidConfigError("Host name too short!")

        try:
            float(self.get_option("SERVICE:FLASK", "timeout"))
        except ValueError:
            raise InvalidConfigError("Timeout is not a number!")
