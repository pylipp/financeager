#!/usr/bin/env python
"""
Module for frontend-backend communication using a flask webservice.
"""

import requests
from flask import Flask
from flask_restful import Api

from .period import Period, TinyDbPeriod
from .config import get_option
from .resources import (PeriodsResource, PeriodResource, EntryResource,
                        CopyResource)


def create_app(config=None):
    """Create web app with RESTful API built from resources."""
    app = Flask(__name__)
    app.config.update(config or {})
    api = Api(app)

    api.add_resource(PeriodsResource, _Proxy.PERIODS_TAIL)
    api.add_resource(CopyResource, _Proxy.COPY_TAIL)
    api.add_resource(PeriodResource,
            "{}/<period_name>".format(_Proxy.PERIODS_TAIL))
    api.add_resource(EntryResource,
        "{}/<period_name>/<table_name>/<eid>".format(_Proxy.PERIODS_TAIL))

    return app


def launch_server(debug=False, host=None):
    """Launch flask webservice application. If the `host` argument is not
    specified, it is read from the configuration.
    """
    try:
        app = create_app(config={
            "DEBUG": debug,
            "SERVER_NAME": host or get_option("SERVICE:FLASK", "host")
            })
        app.run()
    except OSError as e:
        # socket binding: address already in use
        print("The financeager server has already been started.")


class _Proxy(object):
    """Converts CL verbs to HTTP request, sends to webservice and returns
    response."""

    PERIODS_TAIL = "/financeager/periods"
    COPY_TAIL = PERIODS_TAIL + "/copy"

    def run(self, command, http_config=None, **data):
        """Run the specified command. If no http_config given, it is read from
        the user config. The data kwargs are passed to the HTTP request.
        'period' and 'table_name' are substituted, if None.

        :return: dict. See Server class for possible keys
        """

        period = data.pop("period", None) or str(Period.DEFAULT_NAME)

        if http_config is None:
            http_config = {}

        host = http_config.get("host", get_option("SERVICE:FLASK", "host"))
        url = "http://{}{}".format(host, self.PERIODS_TAIL)
        period_url = "{}/{}".format(url, period)

        username = http_config.get("username",
                                   get_option("SERVICE:FLASK", "username"))
        password = http_config.get("password",
                                   get_option("SERVICE:FLASK", "password"))
        auth = None
        if username and password:
            auth = (username, password)

        kwargs = dict(data=data or None, auth=auth,
                      timeout=int(get_option("SERVICE:FLASK", "timeout")))

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
            response = requests.post(
                url.replace(self.PERIODS_TAIL, self.COPY_TAIL), **kwargs)
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
            return {"error": "Unknown command: {}".format(command)}

        return response.json()


def proxy():
    # all communication modules require this function
    return _Proxy()


# catch all exceptions when running proxy in Cli
CommunicationError = Exception
