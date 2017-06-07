#!/usr/bin/env python
"""
Module for frontend-backend communication using a flask webservice.
"""

import sys
import subprocess
import os
import time

import requests
from flask import Flask
from flask_restful import Api

from .period import Period, TinyDbPeriod
from .config import CONFIG
from .resources import (PeriodsResource, PeriodResource,
        EntryResource, ShutdownResource)


def create_app(config=None):
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
    """
    Launch flask webservice via script.

    :return: corresponding ``subprocess.Popen`` object
    """
    server_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "start_webservice.py")
    process = subprocess.call([sys.executable, server_script_path])


class _Proxy(object):
    """
    Converts CL verbs to HTTP request, sends to webservice and returns response.

    :return: dict
    """

    PERIODS_TAIL = "/financeager/periods"

    def run(self, command, **kwargs):
        period = kwargs.pop("period", None) or str(Period.DEFAULT_NAME)
        url = "http://{}:5000{}".format(
                CONFIG["SERVICE:FLASK"]["host"], self.PERIODS_TAIL
                )
        period_url = "{}/{}".format(url, period)

        if command == "print":
            response = requests.get(period_url)
        elif command == "rm":
            eid = kwargs.get("eid")
            if eid is None:
                response = requests.delete(period_url, data=kwargs)
            else:
                response = requests.delete("{}/{}/{}".format(
                    period_url, kwargs.get("table_name", TinyDbPeriod.DEFAULT_TABLE), kwargs.get("eid")))
        elif command == "add":
            response = requests.post(period_url, data=kwargs)
        elif command == "list":
            response = requests.post(url, data=kwargs)
        elif command == "get":
            response = requests.get("{}/{}/{}".format(
                period_url, kwargs.get("table_name", TinyDbPeriod.DEFAULT_TABLE), kwargs.get("eid")))
        else:
            return {"error": "Unknown command: {}".format(command)}

        return response.json()


def proxy():
    # all communication modules require this function
    return _Proxy()


# catch all exceptions when running proxy in Cli
CommunicationError = Exception
