# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import subprocess
import Pyro4
import os
from financeager.period import Period
from financeager.server import Server

class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        python_exec = os.path.join(
                os.environ['WORKON_HOME'], "financeager", "bin", "python")
        self._get_lock("financeager_ns", "{} -m Pyro4.naming".format(python_exec))
        period_name = self._cl_kwargs["period"]
        if period_name is None:
            period_name = Period.DEFAULT_NAME
        self._server_name = Server.NAME_STUB.format(period_name)
        server_script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "start_server.py")
        self._get_lock(self._server_name,
            "python {} {}".format(server_script_path, period_name))

    def _get_lock(self, name, cmd):
        self._lock_socket = socket.socket(socket.AF_UNIX,
                socket.SOCK_DGRAM)
        try:
            self._lock_socket.bind('\0' + name)
            subprocess.Popen(cmd.split())
        except socket.error:
            self._lock_socket.close()
            pass

    def __call__(self):
        server = Pyro4.Proxy("PYRONAME:{}".format(self._server_name))
        command = self._cl_kwargs.pop("command")
        server.run(command, **self._cl_kwargs)
        server.dump()
