"""Module for storing client requests when server not available, and recovering
of such.
"""

import os.path
import json
import traceback

from . import CONFIG_DIR
from .communication import run


OFFLINE_FILEPATH = os.path.join(CONFIG_DIR, "offline.json")


def _load(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            content = json.load(file)
    else:
        content = []

    return content


def _write(content, filepath):
    with open(filepath, "w") as file:
        json.dump(content, file)


def _recover_data(proxy, content):
    """Recover the data items in the content list by running the commands via
    the proxy. If a CommunicationError occurs during recovery, the data being
    currently processed is returned.
    The content list is modified in-place.
    """

    while len(content):
        data = content.pop()
        try:
            run(proxy, **data)
        except Exception as e:
            traceback.print_exc()
            return data


class OfflineRecoveryError(Exception):
    pass


def add(command, offline_filepath=None, **cl_kwargs):
    """Add a command and optional kwargs passed from the command line to the
    offline backup database.

    Non-modifying request commands such as 'print' or 'list' are not stored.

    :return: if anything was added
    """

    if command not in ["add", "rm", "update"]:
        return False

    offline_filepath = offline_filepath or OFFLINE_FILEPATH
    content = _load(offline_filepath)

    cl_kwargs["command"] = command
    content.append(cl_kwargs)
    _write(content, offline_filepath)

    return True


def recover(proxy, offline_filepath=None):
    """Recover the offline backup by passing its content to the given proxy.
    The recovery will be aborted if a CommunicationError occurs.

    If the recovery succeeded, the backup file is deleted.

    :return: if anything was recovered
    :raises: OfflineRecoveryError if recovery failed
    """

    offline_filepath = offline_filepath or OFFLINE_FILEPATH

    content = _load(offline_filepath)
    if not content:
        return False

    failed_recovery_data = _recover_data(proxy, content)

    if failed_recovery_data is None:
        os.remove(offline_filepath)
    else:
        content.append(failed_recovery_data)
        _write(content, offline_filepath)
        raise OfflineRecoveryError()

    return True
