"""Service-agnostic communication-related interface."""
import importlib
from collections import namedtuple
import traceback

import financeager

from . import listing
from . import entries
from .exceptions import InvalidRequest, CommunicationError


def module(name):
    """Return the client module corresponding to the service specified by 'name'
    ('flask' or 'none').
    """
    frontend_modules = {
        "flask": "httprequests",
        "none": "localserver",
    }
    return importlib.import_module("financeager.{}".format(
        frontend_modules[name]))


class Client:
    """Abstract interface for communicating with the service.
    Output is passed to distinct sinks which are functions taking a single
    string argument.
    """

    # Output sinks
    Out = namedtuple("Out", ["info", "error"])

    def __init__(self, *, configuration, out):
        """Set up proxy according to configuration.
        Store the output sinks specified in the Client.Out object 'out'.
        """
        service_name = configuration.get_option("SERVICE", "name")
        proxy_kwargs = {}
        if service_name == "flask":
            proxy_kwargs["http_config"] = configuration.get_option(
                "SERVICE:FLASK")
        else:  # 'none' is the only other option
            proxy_kwargs["data_dir"] = financeager.DATA_DIR

        self.proxy = module(service_name).proxy(**proxy_kwargs)
        self.configuration = configuration
        self.out = out

    def safely_run(self, command, **params):
        """Execute run() while handling any errors. Return indicators about
        whether execution was successful, and whether to store the requested
        command offline, if execution failed due to a service-sided error.
        """
        store_offline = False
        success = False

        try:
            self.out.info(self.run(command, **params))
            success = True
        except InvalidRequest as e:
            # Command is erroneous and hence not stored offline
            self.out.error(e)
        except CommunicationError as e:
            self.out.error(e)
            store_offline = True
        except Exception:
            self.out.error("Unexpected error: {}".format(
                traceback.format_exc()))
            store_offline = True

        return success, store_offline

    def run(self, command, **params):
        """Form and send request to the proxy, and eventually return formatted
        response.

        :raises: CommunicationError, InvalidRequest
        :return: str
        """
        # Extract formatting options; irrelevant, event confusing for Server
        formatting_options = {}
        if command == "list":
            for option in ["stacked_layout", "entry_sort", "category_sort"]:
                formatting_options[option] = params.pop(option)

        response = self.proxy.run(command, **params)

        return _format_response(
            response,
            command,
            default_category=self.configuration.get_option(
                "FRONTEND", "default_category"),
            **formatting_options)


def _format_response(response, command, **listing_options):
    """Format the given response into human-readable text.
    If the response does not contain any of the fields 'id', 'elements',
    'element', or 'periods', the empty string is returned.
    The 'listing_options' are passed to listing.prettify().

    :return: str
    """
    eid = response.get("id")
    if eid is not None:
        verb = {
            "add": "Added",
            "update": "Updated",
            "rm": "Removed",
            "copy": "Copied"
        }[command]
        return "{} element {}.".format(verb, eid)

    elements = response.get("elements")
    if elements is not None:
        return listing.prettify(elements, **listing_options)

    element = response.get("element")
    if element is not None:
        return entries.prettify(
            element, default_category=listing_options["default_category"])

    periods = response.get("periods")
    if periods is not None:
        return "\n".join([p for p in periods])

    return ""
