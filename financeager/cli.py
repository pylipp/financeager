# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import socket
import subprocess
import Pyro4
import os
import sys
from financeager.period import Period
from financeager.server import Server

def launch_server():
    def _get_lock(name, cmd):
        _get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            _get_lock._lock_socket.bind('\0' + name)
            subprocess.Popen(cmd.split())
        except socket.error:
            pass
    return _get_lock

class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        launch_server()("financeager_ns",
                "{} -m Pyro4.naming".format(sys.executable))

        period_name = self._cl_kwargs.get("period")
        if period_name is None:
            period_name = Period.DEFAULT_NAME
        period_name = str(period_name)
        self._server_name = Server.NAME_STUB.format(period_name)
        server_script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "start_server.py")
        launch_server()(self._server_name,
                ' '.join([sys.executable, server_script_path, period_name]))

    def __call__(self):
        server = Pyro4.Proxy("PYRONAME:{}".format(self._server_name))
        command = self._cl_kwargs.pop("command")
        server.run(command, **self._cl_kwargs)
