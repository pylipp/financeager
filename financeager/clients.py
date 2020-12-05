"""Infrastructure for backend communication."""
import traceback
from collections import namedtuple

import financeager

from . import exceptions, localserver, plugin

logger = financeager.init_logger(__name__)


def create(*, configuration, sinks, plugins):
    """Factory to create the Client subclass suitable to the given
    configuration.
    Clients of service plugins are taken into account if specified.
    The sinks are passed into the Client.
    """
    clients = {
        "local": LocalServerClient,
    }

    plugins = plugins or []
    for p in plugins:
        if isinstance(p, plugin.ServicePlugin):
            clients[p.name] = p.client

    service_name = configuration.get_option("SERVICE", "name")
    client_class = clients[service_name]

    return client_class(configuration=configuration, sinks=sinks)


class Client:
    """Abstract interface for communicating with the service.
    Output is directed to distinct sinks which are functions taking a single
    string argument.
    """

    Sinks = namedtuple("Sinks", ["info", "error"])

    def __init__(self, *, configuration, sinks):
        """Store the specified configuration and sinks as attributes.
        The subclass implementation must set up the proxy.
        """
        self.proxy = None
        self.configuration = configuration
        self.sinks = sinks
        self.latest_exception = None

    def safely_run(self, command, **params):
        """Execute self.proxy.run() while handling any errors.
        A caught exception is stored in the 'latest_exception' attribute.
        Return whether execution was successful.

        :return: bool
        """
        success = False

        try:
            self.sinks.info(self.proxy.run(command, **params))
            self.latest_exception = None
            success = True
        except exceptions.InvalidRequest as e:
            self.sinks.error(e)
            self.latest_exception = e

        except exceptions.CommunicationError as e:
            self.sinks.error(e)
            self.latest_exception = e

        except Exception as e:
            self.sinks.error("Unexpected error: {}".format(
                traceback.format_exc()))
            self.latest_exception = e

        return success

    def shutdown(self):
        """Routine to run at the end of the Client lifecycle."""


class LocalServerClient(Client):
    """Client for communicating with the financeager localserver."""

    def __init__(self, *, configuration, sinks):
        """Set up proxy."""
        super().__init__(configuration=configuration, sinks=sinks)

        self.proxy = localserver.Proxy(data_dir=financeager.DATA_DIR)

    def shutdown(self):
        """Instruct stopping of Server."""
        self.proxy.run("stop")
