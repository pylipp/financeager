"""
Module containing top layer of backend communication.
"""
from datetime import datetime

import financeager.fflask
import financeager.server
from . import PERIOD_DATE_FORMAT
from .config import get_option
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


def run(proxy, command, **kwargs):
    """Run a command on the given proxy. The kwargs are passed on. This might
    raise a CommunicationError. Returns formatted server response.
    """
    # pop kwargs that are for formatting at the frontend, not for the server
    stacked_layout = kwargs.pop("stacked_layout", False)
    entry_sort_key = kwargs.pop("entry_sort", CategoryEntry.BASE_ENTRY_SORT_KEY)
    category_sort_key = kwargs.pop("category_sort",
                                   Model.CATEGORY_ENTRY_SORT_KEY)
    _preprocess(kwargs)
    response = proxy.run(command, **kwargs)

    error = response.get("error")
    if error is not None:
        return ERROR_MESSAGE.format(command, error)

    elements = response.get("elements")
    if elements is not None:
        CategoryEntry.BASE_ENTRY_SORT_KEY = entry_sort_key
        CategoryEntry.DEFAULT_NAME = get_option("FRONTEND", "default_category")
        Model.CATEGORY_ENTRY_SORT_KEY = category_sort_key
        return prettify(elements, stacked_layout)

    element = response.get("element")
    if element is not None:
        return prettify_element(element,
                recurrent=kwargs.get("table_name") == "recurrent")

    periods = response.get("periods")
    if periods is not None:
        return "\n".join([p for p in periods])

    return ""


def _preprocess(data):
    """Preprocess data to be passed to server (e.g. convert date format). Raises
    PreprocessError if preprocessing failed.
    """
    date = data.get("date")
    if date is not None:
        try:
            date = datetime.strptime(date, get_option("FRONTEND", "date_format")
                                     ).strftime(PERIOD_DATE_FORMAT)
            data["date"] = date
        except ValueError:
            raise PreprocessingError("Invalid date format.")


class PreprocessingError(Exception):
    pass
