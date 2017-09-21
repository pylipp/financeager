"""
Module containing top layer of backend communication.
"""

import financeager.pyro
import financeager.fflask
import financeager.server
from .config import CONFIG
from .model import prettify
from .entries import prettify as prettify_element


def module():
    """Return the backend module specified by the configuration. Should be one
    of 'flask', 'pyro' or 'none'.
    """
    backend = CONFIG["SERVICE"]["name"]
    backend_modules = {
            "flask": "fflask",
            "pyro": "pyro",
            "none": "server"
            }
    return getattr(financeager, backend_modules[backend])


ERROR_MESSAGE = "Command '{}' returned an error: {}"


def run(proxy, command, **kwargs):
    """Run a command on the given proxy. The kwargs are passed on. This might
    raise a CommunicationError. Returns formatted server response.
    """
    stacked_layout = kwargs.pop("stacked_layout", False)
    response = proxy.run(command, **kwargs)

    if not isinstance(response, dict):
        return ""

    error = response.get("error")
    if error is not None:
        return ERROR_MESSAGE.format(command, error)

    elements = response.get("elements")
    if elements is not None:
        return prettify(elements, stacked_layout)

    element = response.get("element")
    if element is not None:
        return prettify_element(element,
                recurrent=kwargs.get("table_name") == "repetitive")

    periods = response.get("periods")
    if periods is not None:
        return "\n".join([p for p in periods])

    return ""
