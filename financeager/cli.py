# -*- coding: utf-8 -*-
"""
Module containing top layer of backend communication.
"""
from __future__ import unicode_literals, print_function

from .config import CONFIG
from financeager import offline, communication, tui


class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs

        self._backend = CONFIG["SERVICE"]["name"]
        self._communication_module = communication.module()

    def __call__(self):
        command = self._cl_kwargs.pop("command")

        if command == "start":
            self._communication_module.launch_server()
            return

        proxy = self._communication_module.proxy()
        try:
            if command == "tui":
                # fetch data to feed TUI
                response = proxy.run("print", **self._cl_kwargs)
                tui.run(response)
            else:
                communication.run(proxy, command, **self._cl_kwargs)

            offline.recover(proxy)

            if self._backend == "none":
                proxy.run("stop")
        except (self._communication_module.CommunicationError) as e:
            print("Error running command '{}': {}".format(command, e))
            offline.add(command, **self._cl_kwargs)
