"""Construction and handling of HTTP requests to communicate with webservice."""
import http
import json

import requests

from . import default_period_name, DEFAULT_TABLE, DEFAULT_HOST, DEFAULT_TIMEOUT
from . import COPY_TAIL, PERIODS_TAIL
from .exceptions import CommunicationError, InvalidRequest


class _Proxy(object):
    """Converts CL verbs to HTTP request, sends to webservice and returns
    response."""

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
        :raise: CommunicationError on e.g. timeouts or server-side errors,
            InvalidRequest on invalid requests
        """

        period = data.pop("period", None) or default_period_name()

        host = self.http_config.get("host", DEFAULT_HOST)
        base_url = "http://{}{}".format(host, PERIODS_TAIL)
        period_url = "{}/{}".format(base_url, period)
        copy_url = "http://{}{}".format(host, COPY_TAIL)
        eid_url = "{}/{}/{}".format(
            period_url,
            data.get("table_name") or DEFAULT_TABLE,
            data.get("eid"))

        username = self.http_config.get("username")
        password = self.http_config.get("password")
        auth = None
        if username and password:
            auth = (username, password)

        kwargs = dict(data=data or None, auth=auth, timeout=DEFAULT_TIMEOUT)

        if command == "print":
            url = period_url
            function = requests.get
        elif command == "rm":
            url = eid_url
            function = requests.delete
        elif command == "add":
            url = period_url
            function = requests.post
        elif command == "list":
            url = base_url
            function = requests.post
        elif command == "copy":
            url = copy_url
            function = requests.post
        elif command == "get":
            url = eid_url
            function = requests.get
        elif command == "update":
            url = eid_url
            function = requests.patch
        else:
            raise ValueError("Unknown command: {}".format(command))

        try:
            response = function(url, **kwargs)
        except requests.RequestException as e:
            raise CommunicationError(
                "Error sending request: {}".format(e))

        if response.ok:
            return response.json()
        else:
            try:
                # Get further information about error (see Server.run)
                error = response.json()["error"]
            except (json.JSONDecodeError, KeyError):
                error = "-"

            status_code = response.status_code
            if 400 <= status_code < 500:
                error_class = InvalidRequest
            else:
                error_class = CommunicationError

            message = "Error handling request. " +\
                "Server returned '{} ({}): {}'".format(
                    http.HTTPStatus(status_code).phrase, status_code, error)

            raise error_class(message)


def proxy(**kwargs):
    # all communication modules require this function
    return _Proxy(**kwargs)
