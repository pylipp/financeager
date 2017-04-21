# -*- coding: utf-8 -*-
"""
Module containing top layer of backend communication.
"""
from __future__ import unicode_literals, print_function

import os

import financeager.pyro
from financeager.period import prettify
from financeager.server import CONFIG_DIR


class Cli(object):

    def __init__(self, cl_kwargs):
        self._cl_kwargs = cl_kwargs
        self._communication_module = getattr(financeager, "pyro")

        self._stacked_layout = self._cl_kwargs.pop("stacked_layout", False)

    def __call__(self):
        command = self._cl_kwargs.pop("command")

        if command == "list":
            self._print_list()
            return

        if command != "stop":
            self._communication_module.launch_server()

        proxy = self._communication_module.proxy()
        try:
            # server should be stateless and not storing response!
            proxy.run(command, **self._cl_kwargs)
            response = proxy.response
            if response is not None:
                error = response.get("error")
                if error is not None:
                    print(error)

                elements = response.get("elements")
                if elements is not None:
                    print(prettify(elements, self._stacked_layout))
        except (self._communication_module.CommunicationError) as e:
            # 'stop' requested but period server not launched
            pass

    def _print_list(self):
        running = self._cl_kwargs.pop("running", False)
        if running:
            for server in self._communication_module.running_servers():
                print(server)
                print()
        else:
            for file in os.listdir(CONFIG_DIR):
                filename, extension = os.path.splitext(file)
                if extension in [".xml", ".json"]:
                    print(filename)
                    print()
