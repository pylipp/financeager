"""
Module for frontend-backend communication using the Pyro4 framework.
"""

import sys
import subprocess
import os
import time

import Pyro4

from financeager.server import PyroServer


Pyro4.config.COMMTIMEOUT = 1.0


def launch_server():
    """
    Launch Pyro4 nameserver. Silence errors if already running.
    Launch PyroServer via starting script if server is not registered yet.
    """
    with open(os.devnull, 'w') as DEVNULL:
        subprocess.Popen("{} -m Pyro4.naming".format(sys.executable).split(),
                stdout=DEVNULL, stderr=subprocess.STDOUT, close_fds=True)

    name_server = Pyro4.locateNS()
    try:
        name_server.lookup(PyroServer.NAME)
    except (Pyro4.naming.NamingError) as e:
        server_script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "start_server.py")
        subprocess.Popen([sys.executable, server_script_path])
        # wait for launch to avoid failure when creating Proxy
        time.sleep(1.1*Pyro4.config.COMMTIMEOUT)


def proxy():
    return Pyro4.Proxy("PYRONAME:{}".format(PyroServer.NAME))


CommunicationError = Pyro4.naming.NamingError
