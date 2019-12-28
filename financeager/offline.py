"""Module for storing client requests when server not available, and recovering
of such.
"""

import os.path
import json

from . import OFFLINE_FILEPATH, init_logger
from .exceptions import OfflineRecoveryError

logger = init_logger(__name__)


def _load(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            content = json.load(file)
            logger.debug("Loaded {}".format(content))
    else:
        content = []

    return content


def _write(content, filepath):
    with open(filepath, "w") as file:
        logger.debug("Writing {}".format(content))
        json.dump(content, file)


def _recover_data(client, content):
    """Recover the data items in the content list by running the commands via
    'client.safely_run'. If an error occurs, the recovery is aborted, and the
    currently processed data is returned.
    The content list is modified in-place.
    """
    while len(content):
        data = content.pop()
        if not client.safely_run(**data):
            return data


def add(command, offline_filepath=None, **cl_kwargs):
    """Add a command and optional kwargs passed from the command line to the
    offline backup database.

    Non-modifying request commands such as 'print' or 'list' are not stored.

    :return: if anything was added
    """

    if command not in ["add", "remove", "update"]:
        return False

    offline_filepath = offline_filepath or OFFLINE_FILEPATH
    content = _load(offline_filepath)

    cl_kwargs["command"] = command
    content.append(cl_kwargs)
    _write(content, offline_filepath)

    return True


def recover(client, offline_filepath=None):
    """Recover the offline backup by passing its content to the given client.
    The recovery will be aborted if a CommunicationError occurs.

    If the recovery succeeded, the backup file is deleted.

    :return: if anything was recovered
    :raises: OfflineRecoveryError if recovery failed
    """

    offline_filepath = offline_filepath or OFFLINE_FILEPATH

    content = _load(offline_filepath)
    if not content:
        return False

    failed_recovery_data = _recover_data(client, content)

    if failed_recovery_data is None:
        os.remove(offline_filepath)
    else:
        content.append(failed_recovery_data)
        _write(content, offline_filepath)
        raise OfflineRecoveryError()

    return True
