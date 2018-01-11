"""
Module containing top layer of backend communication.
"""
from datetime import datetime

import financeager.fflask
import financeager.server
from . import PERIOD_DATE_FORMAT
from .model import prettify, Model
from .entries import prettify as prettify_element
from .entries import CategoryEntry


def module(name):
    """Return the backend module specified by 'name' ('flask' or 'none')."""
    backend_modules = {
            "flask": "fflask",
            "none": "server",
            }
    return getattr(financeager, backend_modules[name])


ERROR_MESSAGE = "Command '{}' returned an error: {}"


def run(proxy, command, default_category=None, date_format=None,
        stacked_layout=False, entry_sort=CategoryEntry.BASE_ENTRY_SORT_KEY,
        category_sort=Model.CATEGORY_ENTRY_SORT_KEY, **kwargs):
    """Run a command on the given proxy. The kwargs are preprocessed and passed
    on.

    :raises: CommunicationError
    :return: str (formatted server response)
    """
    _preprocess(kwargs, date_format)
    response = proxy.run(command, **kwargs)

    error = response.get("error")
    if error is not None:
        return ERROR_MESSAGE.format(command, error)

    elements = response.get("elements")
    if elements is not None:
        CategoryEntry.BASE_ENTRY_SORT_KEY = entry_sort
        CategoryEntry.DEFAULT_NAME = default_category
        Model.CATEGORY_ENTRY_SORT_KEY = category_sort
        return prettify(elements, stacked_layout)

    element = response.get("element")
    if element is not None:
        return prettify_element(element,
                recurrent=kwargs.get("table_name") == "recurrent")

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
    if date is not None:
        try:
            date = datetime.strptime(date, date_format).strftime(
                PERIOD_DATE_FORMAT)
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
            data["filters"] = parsed_items
        except ValueError:
            # splitting returned less than two parts due to missing separator
            raise PreprocessingError("Invalid filter format: {}".format(item))


class PreprocessingError(Exception):
    pass
