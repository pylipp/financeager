"""Backend-agnostic communication-related routines (preprocessing of requests,
formatting of responses)."""
from datetime import datetime
import importlib

import financeager

from . import PERIOD_DATE_FORMAT
from .listing import prettify, Listing
from .entries import prettify as prettify_element
from .entries import CategoryEntry
from .exceptions import PreprocessingError


def module(name):
    """Return the client module corresponding to the backend specified by 'name'
    ('flask' or 'none').
    """
    frontend_modules = {
        "flask": "httprequests",
        "none": "localserver",
    }
    return importlib.import_module("financeager.{}".format(
        frontend_modules[name]))


class Client:
    def __init__(self, *, configuration, backend_name):
        """Set up proxy according to backend_name and configuration."""
        proxy_kwargs = {}
        if backend_name == "flask":
            proxy_kwargs["http_config"] = configuration.get_option(
                "SERVICE:FLASK")
        else:  # 'none' is the only other option
            proxy_kwargs["data_dir"] = financeager.DATA_DIR

        self.proxy = module(backend_name).proxy(**proxy_kwargs)
        self.configuration = configuration

    def run(self,
            command,
            stacked_layout=False,
            entry_sort=CategoryEntry.BASE_ENTRY_SORT_KEY,
            category_sort=Listing.CATEGORY_ENTRY_SORT_KEY,
            **kwargs):
        """Preprocess parameters, form and send request to the proxy, and
        eventually return formatted response.
        Handle any errors occurring during execution.

        :raises: PreprocessingError, CommunicationError, InvalidRequest
        :return: str
        """
        date_format = self.configuration.get_option("FRONTEND", "date_format")
        _preprocess(kwargs, date_format)

        response = self.proxy.run(command, **kwargs)

        return _format_response(
            response,
            command,
            default_category=self.configuration.get_option(
                "FRONTEND", "default_category"),
            stacked_layout=stacked_layout,
            entry_sort=entry_sort,
            category_sort=category_sort,
            table_name=kwargs.get("table_name"))


def _format_response(response,
                     command,
                     default_category=CategoryEntry.DEFAULT_NAME,
                     stacked_layout=False,
                     entry_sort=CategoryEntry.BASE_ENTRY_SORT_KEY,
                     category_sort=Listing.CATEGORY_ENTRY_SORT_KEY,
                     table_name=None):
    """Format the given response into human-readable text.
    If the response does not contain any of the fields 'id', 'elements',
    'element', or 'periods', the empty string is returned.

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
        Listing.CATEGORY_ENTRY_SORT_KEY = category_sort
        return prettify(elements, stacked_layout)

    element = response.get("element")
    if element is not None:
        CategoryEntry.DEFAULT_NAME = default_category
        return prettify_element(element, recurrent=table_name == "recurrent")

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
