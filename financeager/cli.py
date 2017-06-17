# -*- coding: utf-8 -*-
"""
Module containing top layer of backend communication.
"""
from __future__ import unicode_literals, print_function

import os

from requests.exceptions import ConnectTimeout

import financeager.pyro
import financeager.fflask
import financeager.server
from .config import CONFIG, CONFIG_DIR
from financeager import offline


class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        self._backend = CONFIG["SERVICE"]["name"]
        backend_modules = {
                "flask": "fflask",
                "pyro": "pyro",
                "none": "server"
                }
        self._communication_module = getattr(financeager,
                backend_modules[self._backend])

    def __call__(self):
        command = self._cl_kwargs.pop("command")

        if command == "start":
            self._communication_module.launch_server()
            return

        proxy = self._communication_module.proxy()
        try:
            financeager.server.run(proxy, command, **self._cl_kwargs)

            offline.recover(proxy)

            if self._backend == "none":
                proxy.run("stop")
        except (self._communication_module.CommunicationError) as e:
            print("Error running command '{}': {}".format(command, e))
            offline.add(command, **self._cl_kwargs)
