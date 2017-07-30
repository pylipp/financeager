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


def launch_server():
    """Launch flask webservice application."""
    try:
        config = dict(
                debug=CONFIG["SERVICE:FLASK"].getboolean("debug"),
                host=CONFIG["SERVICE:FLASK"]["host"]
                )
        # FIXME debug config is not taken into account, however repetitive
        # starts are possible. This does not work when passing config kwargs to
        # app.run()
        app = create_app(config=config)
        app.run()
    except OSError as e:
        # socket binding: address already in use
        print("The financeager server has already been started.")


class _Proxy(object):
    """
    Converts CL verbs to HTTP request, sends to webservice and returns response.

    :return: dict
    """

    PERIODS_TAIL = "/financeager/periods"

    def run(self, command, **data):
        period = data.pop("period", None) or str(Period.DEFAULT_NAME)
        url = "http://{}{}".format(
                CONFIG["SERVICE:FLASK"]["host"], self.PERIODS_TAIL
                )
        period_url = "{}/{}".format(url, period)

        username = CONFIG["SERVICE:FLASK"].get("username")
        password = CONFIG["SERVICE:FLASK"].get("password")
        auth = None
        if username is not None and password is not None:
            auth = (username, password)

        kwargs = dict(data=data or None, auth=auth, timeout=5)

        if command == "print":
            response = requests.get(period_url, **kwargs)
        elif command == "rm":
            eid = data.get("eid")
            if eid is None:
                response = requests.delete(period_url, **kwargs)
            else:
                response = requests.delete("{}/{}/{}".format(
                    period_url, data.get("table_name", TinyDbPeriod.DEFAULT_TABLE),
                    eid), **kwargs)
        elif command == "add":
            response = requests.post(period_url, **kwargs)
        elif command == "list":
            response = requests.post(url, **kwargs)
        elif command == "get":
            response = requests.get("{}/{}/{}".format(
                period_url, data.get("table_name", TinyDbPeriod.DEFAULT_TABLE),
                data.get("eid")), **kwargs)
        else:
            return {"error": "Unknown command: {}".format(command)}

        return response.json()


def proxy():
    # all communication modules require this function
    return _Proxy()


# catch all exceptions when running proxy in Cli
CommunicationError = Exception
