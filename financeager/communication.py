"""Service-agnostic communication-related interfaces wrapping several routines
(preprocessing of requests, formatting of responses)."""
from datetime import datetime
import importlib
from collections import namedtuple

import financeager

from . import PERIOD_DATE_FORMAT
from .listing import prettify
from .entries import prettify as prettify_element
from .entries import CategoryEntry
from .exceptions import PreprocessingError, InvalidRequest, CommunicationError


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
        except (PreprocessingError, InvalidRequest) as e:
            # Command is erroneous and hence not stored offline
            self.out.error(e)
        except CommunicationError as e:
            self.out.error(e)
            store_offline = True
        except Exception:
            self.out.exception("Unexpected error")
            store_offline = True

        return success, store_offline

    def run(self, command, **params):
        """Preprocess parameters, form and send request to the proxy, and
        eventually return formatted response.

        :raises: PreprocessingError, CommunicationError, InvalidRequest
        :return: str
        """
        # Extract formatting options; irrelevant, event confusing for Server
        formatting_options = {}
        if command == "print":
            for option in ["stacked_layout", "entry_sort", "category_sort"]:
                formatting_options[option] = params.pop(option)

        date_format = self.configuration.get_option("FRONTEND", "date_format")
        _preprocess(params, date_format)

        response = self.proxy.run(command, **params)

        return _format_response(
            response,
            command,
            default_category=self.configuration.get_option(
                "FRONTEND", "default_category"),
            **formatting_options)


def _format_response(response,
                     command,
                     default_category=CategoryEntry.DEFAULT_NAME,
                     stacked_layout=False,
                     entry_sort=CategoryEntry.BASE_ENTRY_SORT_KEY,
                     **listing_options):
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
        CategoryEntry.BASE_ENTRY_SORT_KEY = entry_sort
        CategoryEntry.DEFAULT_NAME = default_category
        return prettify(elements, stacked_layout, **listing_options)

    element = response.get("element")
    if element is not None:
        CategoryEntry.DEFAULT_NAME = default_category
        return prettify_element(element)

    periods = response.get("periods")
    if periods is not None:
        return "\n".join([p for p in periods])

    return ""


def _preprocess(data, date_format=None):
    """Preprocess data to be passed to server (e.g. convert date format, parse
    'filters' options passed with print command). Raises PreprocessError if
    preprocessing failed.
    """
    date = data.get("date")
    # recovering offline data does not bring any date format because the data
    # has already been converted
    if date is not None and date_format is not None:
        try:
            date = datetime.strptime(date,
                                     date_format).strftime(PERIOD_DATE_FORMAT)
            data["date"] = date
        except ValueError:
            raise PreprocessingError("Invalid date format.")

    filter_items = data.get("filters")
    if filter_items is not None:
        # convert list of "key=value" strings into dictionary
        parsed_items = {}
        try:
            for item in filter_items:
                key, value = item.split("=")
                parsed_items[key] = value.lower()

            try:
                # Substitute category default name
                if parsed_items["category"] == CategoryEntry.DEFAULT_NAME:
                    parsed_items["category"] = None
            except KeyError:
                # No 'category' field present
                pass

            data["filters"] = parsed_items
        except ValueError:
            # splitting returned less than two parts due to missing separator
            raise PreprocessingError("Invalid filter format: {}".format(item))
