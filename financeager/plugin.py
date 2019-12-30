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


class PluginBase:
    def __init__(self, *, name, config):
        """Set plugin name and config (a PluginConfiguration instance)."""
        self.name = name
        self.config = config


class ServicePlugin(PluginBase):
    """Container for a financeager.services plugin.
    When developing a service plugin, provide a Client class required for
    communication with the service.
    """

    def __init__(self, *, name, config, client):
        super().__init__(name=name, config=config)
        self.client = client
