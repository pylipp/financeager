"""Running HTTP requests to communicate with webservice."""
import http
import json

import requests

from .period import Period, TinyDbPeriod
from .fflask import COPY_TAIL, PERIODS_TAIL


class _Proxy(object):
    """Converts CL verbs to HTTP request, sends to webservice and returns
    response."""

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_TIMEOUT = 10

    def __init__(self, http_config=None):
        """http_config: dict specifying host and (optionally) username/password
        for basic auth
        """
        self.http_config = http_config or {}

    def run(self, command, **data):
        """Run the specified command. If no http_config given, it is read from
        the user config. The data kwargs are passed to the HTTP request.
        'period' and 'table_name' are substituted, if None.

        :return: dict. See Server class for possible keys
        :raise: ValueError if invalid command given
        :raise: CommunicationError if HTTP response not ok
        """

        period = data.pop("period", None) or Period.DEFAULT_NAME

        host = self.http_config.get("host", self.DEFAULT_HOST)
        url = "http://{}{}".format(host, PERIODS_TAIL)
        period_url = "{}/{}".format(url, period)
        copy_url = "http://{}{}".format(host, COPY_TAIL)

        username = self.http_config.get("username")
        password = self.http_config.get("password")
        auth = None
        if username and password:
            auth = (username, password)

        kwargs = dict(data=data or None, auth=auth,
                      timeout=self.DEFAULT_TIMEOUT)

        if command == "print":
            response = requests.get(period_url, **kwargs)
        elif command == "rm":
            response = requests.delete("{}/{}/{}".format(
                period_url,
                data.get("table_name") or TinyDbPeriod.DEFAULT_TABLE,
                data.get("eid")), **kwargs)
        elif command == "add":
            response = requests.post(period_url, **kwargs)
        elif command == "list":
            response = requests.post(url, **kwargs)
        elif command == "copy":
            response = requests.post(copy_url, **kwargs)
        elif command == "get":
            response = requests.get("{}/{}/{}".format(
                period_url,
                data.get("table_name") or TinyDbPeriod.DEFAULT_TABLE,
                data.get("eid")), **kwargs)
        elif command == "update":
            response = requests.patch("{}/{}/{}".format(
                period_url,
                data.get("table_name") or TinyDbPeriod.DEFAULT_TABLE,
                data.get("eid")), **kwargs)
        else:
            raise ValueError("Unknown command: {}".format(command))

        if response.ok:
            return response.json()
        else:
            try:
                # Get further information about error (see Server.run)
                error = response.json()["error"]
            except (json.JSONDecodeError, KeyError):
                error = "-"

            raise CommunicationError(
                "Error making request. Server returned '{} ({}): {}'".format(
                    http.HTTPStatus(response.status_code).phrase,
                    response.status_code, error))


def proxy(**kwargs):
    # all communication modules require this function
    return _Proxy(**kwargs)


class CommunicationError(Exception):
    pass
