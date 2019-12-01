"""Construction and handling of HTTP requests to communicate with webservice."""
import http
import json

import requests

from . import default_period_name, DEFAULT_TABLE, DEFAULT_HOST, DEFAULT_TIMEOUT
from . import COPY_TAIL, PERIODS_TAIL
from .exceptions import CommunicationError, InvalidRequest


class Proxy:
    """Proxy for communicating with webservice via HTTP."""

    def __init__(self, http_config=None):
        """Args:
        http_config (dict): HTTP configuration with fields 'host' (default:
            DEFAULT_HOST), 'timeout' (default: DEFAULT_TIMEOUT) and
            optionally 'username'/'password' (for basic auth)
        """
        self.http_config = http_config or {}

    def run(self, command, **data):
        """Convert specified command and data into HTTP request, send it to
        webservice, and return response. Handle error responses.
        The data kwargs are passed to the HTTP request.
        'period' and 'table_name' data fields are substituted, if None.

        :return: dict. See Server class for possible keys
        :raise: ValueError if invalid command given
        :raise: CommunicationError on e.g. timeouts or server-side errors,
            InvalidRequest on invalid requests
        """

        period = data.pop("period", None) or default_period_name()

        host = self.http_config.get("host", DEFAULT_HOST)
        base_url = "{}{}".format(host, PERIODS_TAIL)
        period_url = "{}/{}".format(base_url, period)
        copy_url = "{}{}".format(host, COPY_TAIL)
        eid_url = "{}/{}/{}".format(period_url,
                                    data.get("table_name") or DEFAULT_TABLE,
                                    data.get("eid"))

        username = self.http_config.get("username")
        password = self.http_config.get("password")
        auth = None
        if username and password:
            auth = (username, password)

        kwargs = dict(auth=auth, timeout=DEFAULT_TIMEOUT)

        if command == "list":
            # Correctly send filters; allowing for server-side deserialization
            kwargs["json"] = json.dumps(data)
        else:
            kwargs["json"] = data or None

        if command == "list":
            url = period_url
            function = requests.get
        elif command == "remove":
            url = eid_url
            function = requests.delete
        elif command == "add":
            url = period_url
            function = requests.post
        elif command == "periods":
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
            raise CommunicationError("Error sending request: {}".format(e))

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
