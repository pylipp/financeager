"""
Module for frontend-backend communication using the Pyro4 framework.
"""

import sys
import subprocess
import os
import time

import Pyro4

from financeager.server import PyroServer
from .config import CONFIG


Pyro4.config.COMMTIMEOUT = 1.0


def launch_server():
    """
    Launch Pyro4 nameserver. Silence errors if already running.
    Launch PyroServer via starting script if server is not registered yet.
    """
    pyro_config = CONFIG["SERVICE:PYRO"]
    hmac_key = pyro_config.get("hmac_key")

    with open(os.devnull, 'w') as DEVNULL:
        hmac_key_option = "-k {}".format(hmac_key) if hmac_key else ""
        command = "pyro4-ns -n {} -p {} {}".format(
                pyro_config["host"],
                pyro_config["ns_port"],
                hmac_key_option
                )
        print("Starting Pyro nameserver via '{}'".format(command))
        subprocess.Popen(command.split())
                # stdout=DEVNULL, stderr=subprocess.STDOUT, close_fds=True)

    name_server = Pyro4.locateNS(hmac_key=hmac_key)
    try:
        name_server.lookup(PyroServer.NAME)
    except (Pyro4.naming.NamingError) as e:
        server_script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "start_server.py")
        subprocess.Popen([sys.executable, server_script_path])
        # wait for launch to avoid failure when creating Proxy
        time.sleep(1.1*Pyro4.config.COMMTIMEOUT)


def proxy():
    proxy = Pyro4.Proxy("PYRONAME:{}".format(PyroServer.NAME))

    # see https://stackoverflow.com/questions/34013578/pyro-how-to-use-hmac-key-with-name-server-communicationerror-hmac-key-config
    proxy._pyroHmacKey = CONFIG.get("SERVICE:PYRO", "hmac_key", fallback=None)

    return proxy


CommunicationError = Pyro4.naming.NamingError
