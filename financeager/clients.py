"""Infrastructure for backend communication."""

import os.path
import traceback
from collections import namedtuple

import financeager

from . import exceptions, init_logger, localserver, plugin

logger = init_logger(__name__)


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
            self.sinks.error(f"Unexpected error: {traceback.format_exc()}")
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

    def safely_run(self, command, **params):
        """Run the parent method, and for certain modifying commands, fetch category
        names from the server and store them in the cache.
        """
        success = super().safely_run(command, **params)
        if command not in ["add", "remove", "update"]:
            return success

        try:
            self._write_categories_for_cli_completion()
        except Exception as e:
            logger.debug(str(e))
        return success

    def _write_categories_for_cli_completion(self):
        # There might be different categories for each pocket. However when reading the
        # cache at the time of building the CLI completion, the target pocket cannot be
        # determined. It's assumed the default pocket is most relevant, hence its
        # contained categories are stored
        categories = self.proxy.run("categories", pocket=None)["categories"]
        fp = os.path.join(financeager.CACHE_DIR, financeager.CATEGORIES_CACHE_FILENAME)
        with open(fp, "w") as f:
            # The category cache is a line-separated list of names
            f.write("\n".join(categories))

    def shutdown(self):
        """Instruct stopping of Server."""
        self.proxy.run("stop")
