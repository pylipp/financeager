"""Service-agnostic communication-related interface."""
import importlib
from collections import namedtuple
import traceback

import financeager

from .exceptions import InvalidRequest, CommunicationError


class Client:
    """Abstract interface for communicating with the service.
    Output is directed to distinct sinks which are functions taking a single
    string argument.
    """

    Sinks = namedtuple("Sinks", ["info", "error"])

    def __init__(self, *, configuration, sinks):
        """Set up proxy according to configuration.
        Store the specified sinks.
        """
        self.service_name = configuration.get_option("SERVICE", "name")
        proxy_kwargs = {}
        if self.service_name == "flask":
            proxy_kwargs["http_config"] = configuration.get_option(
                "SERVICE:FLASK")
            proxy_module_name = "httprequests"
            financeager.init_logger("urllib3")

        else:  # 'none' is the only other option
            proxy_kwargs["data_dir"] = financeager.DATA_DIR
            proxy_module_name = "localserver"

        module = importlib.import_module(
            "financeager.{}".format(proxy_module_name))
        self.proxy = module.proxy(**proxy_kwargs)
        self.configuration = configuration
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
        if self.service_name == "none":
            self.proxy.run("stop")
