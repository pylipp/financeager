#!/usr/bin/env python
"""Utility script to start flask webservice. Mainly for testing purposes."""

import argparse
import os.path

from financeager.fflask import launch_server
from financeager.config import Configuration
from financeager import CONFIG_DIR

if __name__ == "__main__":
    start_parser = argparse.ArgumentParser(description=globals()["__doc__"])

    start_parser.add_argument(
        "-d", "--debug", action="store_true", help="start flask in debug mode")
    start_parser.add_argument(
        "-i",
        "--host-ip",
        default=None,
        dest="host",
        help="IP address and port of server, format 'XXX.XXX.XXX.XXX:port'.  "
        "If not specified, it is attempted to read the value from the config "
        "file.")
    start_parser.add_argument(
        "-C",
        "--config",
        help="path to config file (default: {}/config".format(CONFIG_DIR))

    cl_options = start_parser.parse_args()

    host = cl_options.host
    if host is None:
        # read variable from config file
        config_filepath = cl_options.config
        if config_filepath is None:
            config_filepath = os.path.join(CONFIG_DIR, "config")
        config = Configuration(filepath=config_filepath)
        host = config.get("SERVICE:FLASK", "host")

    launch_server(debug=cl_options.debug, host=host)
