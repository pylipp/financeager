"""Service-agnostic communication-related interface."""
from collections import namedtuple
import traceback

import financeager
from . import httprequests, localserver, offline
from .exceptions import InvalidRequest, CommunicationError, OfflineRecoveryError


def client(*, configuration, sinks):
    """Factory to create the Client subclass suitable to the given
    configuration. The sinks are passed into the Client.
    """
    service_name = configuration.get_option("SERVICE", "name")

    if service_name == "flask":
        client_class = FlaskClient
    else:  # 'none' is the only other option
        client_class = LocalServerClient

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

    def safely_run(self, command, **params):
        """Execute self.proxy.run() while handling any errors. Return indicators
        about whether execution was successful, and whether to store the
        requested command offline, if execution failed due to a service-sided
        error.

        :return: tuple(bool, bool)
        """
        store_offline = False
        success = False

        try:
            self.sinks.info(self.proxy.run(command, **params))
            success = True
        except InvalidRequest as e:
            # Command is erroneous and hence not stored offline
            self.sinks.error(e)
        except CommunicationError as e:
            self.sinks.error(e)
            store_offline = True
        except Exception:
            self.sinks.error("Unexpected error: {}".format(
                traceback.format_exc()))
            store_offline = True

        return success, store_offline

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

    def safely_run(self, command, **params):
        """Execute base functionality.
        If successful, attempt to recover offline backup. Otherwise store
        request in offline backup.

        :return: tuple(bool, bool)
        """
        success, store_offline = super().safely_run(command, **params)

        if success:
            try:
                if offline.recover(super()):
                    self.sinks.info("Recovered offline backup.")
            except OfflineRecoveryError:
                self.sinks.error("Offline backup recovery failed!")
                success = False

        if store_offline and offline.add(command, **params):
            self.sinks.info(
                "Stored '{}' request in offline backup.".format(command))

        return success, store_offline


class LocalServerClient(Client):
    """Client for communicating with the financeager localserver."""

    def __init__(self, *, configuration, sinks):
        """Set up proxy."""
        super().__init__(sinks=sinks)

        self.proxy = localserver.Proxy(data_dir=financeager.DATA_DIR)

    def shutdown(self):
        """Instruct stopping of Server."""
        self.proxy.run("stop")
