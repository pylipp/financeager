#!/usr/bin/env python
"""
Module for frontend-backend communication using a flask webservice.
"""

import sys
import subprocess
import os

import requests

from financeager.period import Period, TinyDbPeriod


def launch_server():
    """
    Launch flask webservice via script.

    :return: corresponding ``subprocess.Popen`` object
    """
    server_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "start_webservice.py")
    return subprocess.Popen([sys.executable, server_script_path])


class _Proxy(object):
    """
    Converts CL verbs to HTTP request, sends to webservice and returns response.

    :return: dict
    """

    def run(self, command, **kwargs):
        period = kwargs.pop("period", None) or str(Period.DEFAULT_NAME)
        url = "http://127.0.0.1:5000/financeager/periods/{}".format(period)

        if command == "print":
            response = requests.get(url)
        elif command == "rm":
            eid = kwargs.get("eid")
            if eid is None:
                response = requests.delete(url, data=kwargs)
            else:
                response = requests.delete("{}/{}/{}".format(
                    url, kwargs.get("table_name", TinyDbPeriod.DEFAULT_TABLE), kwargs.get("eid")))
        elif command == "add":
            response = requests.post(url, data=kwargs)
        elif command == "list":
            response = requests.get("http://127.0.0.1:5000/financeager/periods")
        elif command == "get":
            response = requests.get("{}/{}/{}".format(
                url, kwargs.get("table_name", TinyDbPeriod.DEFAULT_TABLE), kwargs.get("eid")))
        elif command == "stop":
            response = requests.post("http://127.0.0.1:5000/financeager/stop")
        else:
            return {"error": "Unknown command: {}".format(command)}

        return response.json()


def proxy():
    # all communication modules require this function
    return _Proxy()


# catch all exceptions when running proxy in Cli
CommunicationError = Exception
