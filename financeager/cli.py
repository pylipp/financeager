# -*- coding: utf-8 -*-
"""
Module containing top layer of backend communication.
"""
from __future__ import unicode_literals, print_function

from .config import CONFIG
from financeager import offline, communication


def main(cl_kwargs):
    command = cl_kwargs.pop("command")
    communication_module = communication.module()

    if command == "start":
        communication_module.launch_server()
        return

    proxy = communication_module.proxy()
    try:
        communication.run(proxy, command, **cl_kwargs)

        offline.recover(proxy)

        if CONFIG["SERVICE"]["name"] == "none":
            proxy.run("stop")
    except (communication_module.CommunicationError) as e:
        print("Error running command '{}': {}".format(command, e))
        offline.add(command, **cl_kwargs)
