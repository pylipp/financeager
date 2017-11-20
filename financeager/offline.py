"""
Module for handling requests when server not available.
"""

import os.path
import json

from .config import CONFIG_DIR, CONFIG
from .communication import run, module


def _load(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            content = json.load(file)
    else:
        content = []

    return content


def add(command, **cl_kwargs):
    """Add a command and optional kwargs passed from the command line to the
    offline backup database.

    Non-modifying request commands such as 'print' or 'list' are not stored.
    """
    if command not in ["add", "rm", "update"]:
        return

    offline_filepath = os.path.join(CONFIG_DIR,
            CONFIG["DATABASE"]["offline_backup"] + ".json")

    content = _load(offline_filepath)
    data = {"command": command, "kwargs": cl_kwargs}
    content.append(data)

    with open(offline_filepath, "w") as file:
        json.dump(content, file)
        print("Stored '{}' request in offline backup.".format(command))


def recover(proxy):
    """Recover the offline backup by passing its content to the given proxy.
    The recovery will be aborted if a CommunicationError occurs. 

    If the recovery succeeded, the backup file is deleted. 
    """
    offline_filepath = os.path.join(CONFIG_DIR,
            CONFIG["DATABASE"]["offline_backup"] + ".json")

    content = _load(offline_filepath)
    if not content:
        return 

    print("Recovering {} item(s) in offline backup...".format(len(content)))

    while len(content):
        item = content.pop()
        try:
            run(proxy, item["command"], **item["kwargs"])
        except module().CommunicationError as e:
            print("Aborting offline backup recovery: {}".format(e))

            content.append(item)
            with open(offline_filepath, "w") as file:
                json.dump(content, file)
            return 

    os.remove(offline_filepath)
