"""Configuration of the financeager application."""
import os.path
from configparser import ConfigParser, NoSectionError, NoOptionError

import financeager
from financeager import plugin
from .entries import CategoryEntry, BaseEntry
from .exceptions import InvalidConfigError
from . import DEFAULT_HOST, DEFAULT_TIMEOUT, init_logger

logger = init_logger(__name__)


class Configuration:
    """Wrapper around a ConfigParser object holding configuration. The default
    configuration can be customized by settings specified in a config file.
    """

    def __init__(self, filepath=None, plugins=None):
        """Initialize the default configuration, overwrite with custom
        configuration from file if available, and eventually validate the loaded
        configuration.
        If plugins are given, their configuration is taken into account.

        :type plugins: list[plugin.PluginBase]

        :raises: InvalidConfigError if validation fails
        """
        if filepath is None and os.path.exists(financeager.CONFIG_FILEPATH):
            self._filepath = financeager.CONFIG_FILEPATH
        else:
            self._filepath = filepath

        self._plugins = plugins or []
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

        for p in self._plugins:
            p.config.init_defaults(self._parser)

    def _load_custom_config(self):
        """Update config values according to customization in config file."""
        if self._filepath is None:
            return

        logger.debug("Loading custom config from {}".format(self._filepath))

        custom_config = ConfigParser()
        # read() silently ignores non-existing paths but returns list of paths
        # that were successfully read
        used_filepaths = custom_config.read(self._filepath)
        if len(used_filepaths) < 1 or used_filepaths[0] != self._filepath:
            raise InvalidConfigError("Config filepath does not exist!")

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
        valid_services = ["none", "flask"]
        for p in self._plugins:
            if isinstance(p, plugin.ServicePlugin):
                valid_services.append(p.name)

        if self.get_option("SERVICE", "name") not in valid_services:
            raise InvalidConfigError("Unknown service name!")

        if len(self.get_option("FRONTEND", "default_category")) < 1:
            raise InvalidConfigError("Default category name too short!")

        for p in self._plugins:
            p.config.validate(self)
