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

    def init_option_types(self, option_types):
        """Specify types of plugin options (int, float, boolean) if conversion
        at the time of retrieving the option is desired. The given dictionary
        should be modified in-place by adding the type to the corresponding
        section and option.
        """

    def validate(self, config):
        """Validate content of the Configuration object specific to the plugin.
        Typed options are implicitly validated for conversion by the
        Configuration object already.
        """


class PluginCliOptions(abc.ABC):
    """Utility to provide CLI options specific to the plugin.
    When developing a plugin, optionally provide an implementation derived from
    this class."""

    @abc.abstractmethod
    def extend(self, command_parser):
        """Extend the 'command' subparser of the financeager CLI by additional commands
        and/or arguments.
        Remember that the corresponding Client class must provide an
        implementation to handle the new commands.
        """


class PluginBase:
    def __init__(self, *, name, config, cli_options=None):
        """Set plugin name, config (a PluginConfiguration instance), and optional CLI
        options (a PluginCliOptions instance)."""
        self.name = name
        self.config = config
        self.cli_options = cli_options


class ServicePlugin(PluginBase):
    """Container for a financeager.services plugin.
    When developing a service plugin, provide a Client class required for
    communication with the service.
    """

    def __init__(self, *, name, config, client, cli_options=None):
        super().__init__(name=name, config=config, cli_options=cli_options)
        self.client = client
