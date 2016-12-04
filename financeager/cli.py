# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import subprocess
import Pyro4
import os
import sys
import time
from financeager.period import Period
from financeager.server import Server

Pyro4.config.COMMTIMEOUT = 1.0

class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        # launch nameserver. Silence errors if already running
        DEVNULL = open(os.devnull, 'w')
        subprocess.Popen("{} -m Pyro4.naming".format(sys.executable).split(),
                stdout=DEVNULL, stderr=subprocess.STDOUT, close_fds=True)

        period_name = self._cl_kwargs.get("period", str(Period.DEFAULT_NAME))
        self._server_name = Server.NAME_STUB.format(period_name)

        name_server = Pyro4.locateNS()
        # launch starting script if period server is not registered yet
        # TODO avoid accidental launching if stop requested
        try:
            name_server.lookup(self._server_name)
        except (Pyro4.naming.NamingError) as e:
            server_script_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), "start_server.py")
            subprocess.Popen([sys.executable, server_script_path, period_name])
            time.sleep(1.1*Pyro4.config.COMMTIMEOUT)

    def __call__(self):
        server = Pyro4.Proxy("PYRONAME:{}".format(self._server_name))
        # TODO pop in server.run()
        command = self._cl_kwargs.pop("command")
        server.run(command, **self._cl_kwargs)
