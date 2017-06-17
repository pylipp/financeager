"""
Module containing top layer of backend communication.
"""

import financeager.pyro
import financeager.fflask
import financeager.server
from .config import CONFIG
from .period import prettify


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


def run(proxy, command, **kwargs):
    """Run a command on the given proxy. The kwargs are passed on. This might
    raise a CommunicationError.
    """
    stacked_layout = kwargs.pop("stacked_layout", False)
    response = proxy.run(command, **kwargs)

    if not isinstance(response, dict):
        return

    error = response.get("error")
    if error is not None:
        print("Command '{}' returned an error: {}".format(command, error))

    elements = response.get("elements")
    if elements is not None:
        print(prettify(elements, stacked_layout))

    periods = response.get("periods")
    if periods is not None:
        for p in periods:
            print(p)
