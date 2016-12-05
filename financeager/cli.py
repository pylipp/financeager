# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import subprocess
import Pyro4
import os
import sys
import time
from financeager.period import Period
from financeager.server import XmlServer

Pyro4.config.COMMTIMEOUT = 1.0

class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        # launch nameserver. Silence errors if already running
        DEVNULL = open(os.devnull, 'w')
        subprocess.Popen("{} -m Pyro4.naming".format(sys.executable).split(),
                stdout=DEVNULL, stderr=subprocess.STDOUT, close_fds=True)

        self._period_name = self._cl_kwargs.get("period", str(Period.DEFAULT_NAME))

    def __call__(self):
        command = self._cl_kwargs.pop("command")
        server_name = XmlServer.name(self._period_name)

        if command != "stop":
            self._start_period_server(server_name)

        server = Pyro4.Proxy("PYRONAME:{}".format(server_name))
        try:
            server.run(command, **self._cl_kwargs)
        except (Pyro4.naming.NamingError) as e:
            # 'stop' requested but corresponding period server not launched
            pass

    def _start_period_server(self, server_name):
        name_server = Pyro4.locateNS()
        # launch starting script if period server is not registered yet
        try:
            name_server.lookup(server_name)
        except (Pyro4.naming.NamingError) as e:
            server_script_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "start_server.py")
            subprocess.Popen(
                    [sys.executable, server_script_path, self._period_name])
            # wait for launch to avoid failure when creating Proxy
            time.sleep(1.1*Pyro4.config.COMMTIMEOUT)
