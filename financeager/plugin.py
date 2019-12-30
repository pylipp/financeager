"""Support for plugin development."""

import abc


class PluginConfiguration(abc.ABC):
    """Utility to provide configuration specific to the plugin.
    When developing a plugin, provide an implementation derived from this
    class."""

    @abc.abstractmethod
    def init_defaults(self, config_parser):
        """Initialize configuration defaults by extending the given ConfigParser
        by relevant sections.
        """

    @abc.abstractmethod
    def validate(self, config):
        """Validate content of the Configuration object specific to the plugin.
        """
