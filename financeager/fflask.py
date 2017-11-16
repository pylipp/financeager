#!/usr/bin/env python
"""
Module for frontend-backend communication using a flask webservice.
"""

import requests
from flask import Flask
from flask_restful import Api

from .period import Period, TinyDbPeriod
from .config import CONFIG
from .resources import (PeriodsResource, PeriodResource,
        EntryResource, ShutdownResource)


def create_app(config=None):
    """Create web app with RESTful API built from resources."""
    app = Flask(__name__)
    app.config.update(config or {})
    api = Api(app)

    api.add_resource(PeriodsResource, _Proxy.PERIODS_TAIL)
    api.add_resource(PeriodResource,
            "{}/<period_name>".format(_Proxy.PERIODS_TAIL))
    api.add_resource(EntryResource,
        "{}/<period_name>/<table_name>/<eid>".format(_Proxy.PERIODS_TAIL))

    return app


def launch_server(**kwargs):
    """Launch flask webservice application."""
    try:
        config = kwargs or dict(
                debug=CONFIG["SERVICE:FLASK"].getboolean("debug"),
                host=CONFIG["SERVICE:FLASK"]["host"]
                )
        app = create_app(config=config)
        app.run()
    except OSError as e:
        # socket binding: address already in use
        print("The financeager server has already been started.")


class _Proxy(object):
    """Converts CL verbs to HTTP request, sends to webservice and returns
    response."""

    PERIODS_TAIL = "/financeager/periods"

    def run(self, command, http_config=None, **data):
        """Run the specified command. If no http_config given, it is read from
        the user config. The data kwargs are passed to the HTTP request.
        'period' and 'table_name' are substituted, if None.

        :return: dict. See Server class for possible keys
        """

        period = data.pop("period", None) or str(Period.DEFAULT_NAME)

        if http_config is None:
            http_config = {}

        host = http_config.get("host", CONFIG["SERVICE:FLASK"]["host"])
        url = "http://{}{}".format(host, self.PERIODS_TAIL)
        period_url = "{}/{}".format(url, period)

        username = http_config.get("username",
                CONFIG["SERVICE:FLASK"].get("username"))
        password = http_config.get("password",
                CONFIG["SERVICE:FLASK"].get("password"))
        auth = None
        if username is not None and password is not None:
            auth = (username, password)

        kwargs = dict(data=data or None, auth=auth,
                timeout=CONFIG["SERVICE:FLASK"].getint("timeout"))

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

        if response.ok:
            return response.json()
        return {"error": "{} {}".format(response.text, response.status_code)}


def proxy():
    # all communication modules require this function
    return _Proxy()


# catch all exceptions when running proxy in Cli
CommunicationError = Exception
