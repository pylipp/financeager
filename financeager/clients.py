"""Infrastructure for backend communication."""
from collections import namedtuple
import traceback

import financeager
from . import httprequests, localserver, offline, plugin
from .exceptions import InvalidRequest, CommunicationError, OfflineRecoveryError

logger = financeager.init_logger(__name__)


def create(*, configuration, sinks, plugins):
    """Factory to create the Client subclass suitable to the given
    configuration.
    Clients of service plugins are taken into account if specified.
    The sinks are passed into the Client.
    """
    clients = {
        "none": LocalServerClient,
        "flask": FlaskClient,
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

    def __init__(self, *, sinks):
        """Store the specified sinks as attributes.
        The subclass implementation must set up the proxy.
        """
        self.proxy = None
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
        except InvalidRequest as e:
            self.sinks.error(e)
            self.latest_exception = e

        except CommunicationError as e:
            self.sinks.error(e)
            self.latest_exception = e

        except Exception as e:
            self.sinks.error("Unexpected error: {}".format(
                traceback.format_exc()))
            self.latest_exception = e

        return success

    def shutdown(self):
        """Routine to run at the end of the Client lifecycle."""


class FlaskClient(Client):
    """Client for communicating with the financeager Flask webservice."""

    def __init__(self, *, configuration, sinks):
        """Set up proxy and urllib3 logger."""
        super().__init__(sinks=sinks)
        self.proxy = httprequests.Proxy(
            http_config=configuration.get_option("SERVICE:FLASK"))

        financeager.init_logger("urllib3")

        logger.warning(
            "Flask-webservice related functionality will be moved to a "
            "dedicated plugin.\n"
            "Check the Changelog when updating your financeager version.")

    def safely_run(self, command, **params):
        """Execute base functionality.
        If successful, attempt to recover offline backup. Otherwise store
        request in offline backup.
        Return whether execution was successful.

        :return: bool
        """
        success = super().safely_run(command, **params)

        if success:
            try:
                # Avoid recursion by passing base class for invoking safely_run
                if offline.recover(super()):
                    self.sinks.info("Recovered offline backup.")

            except OfflineRecoveryError:
                self.sinks.error("Offline backup recovery failed!")
                success = False

        # If request was erroneous, it's not supposed to be stored offline
        if not isinstance(self.latest_exception, InvalidRequest) and\
                self.latest_exception is not None and\
                offline.add(command, **params):
            self.sinks.info(
                "Stored '{}' request in offline backup.".format(command))

        return success


class LocalServerClient(Client):
    """Client for communicating with the financeager localserver."""

    def __init__(self, *, configuration, sinks):
        """Set up proxy."""
        super().__init__(sinks=sinks)

        self.proxy = localserver.Proxy(data_dir=financeager.DATA_DIR)

    def shutdown(self):
        """Instruct stopping of Server."""
        self.proxy.run("stop")
