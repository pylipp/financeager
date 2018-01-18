#!/usr/bin/env python

"""Utility script to start flask webservice. Mainly for testing purposes."""

import argparse

from financeager.cli import get_option
from financeager.fflask import launch_server


if __name__ == "__main__":
    start_parser = argparse.ArgumentParser(description=globals()["__doc__"])

    start_parser.add_argument(
        "-d", "--debug", action="store_true", help="start flask in debug mode")
    start_parser.add_argument(
        "-i", "--host-ip", default=None, dest="host",
        help="IP address and port of server, format 'XXX.XXX.XXX.XXX:port'.  "
        "If not specified, it is attempted to read the value from the config "
        "file.")

    cl_options = start_parser.parse_args()

    host = cl_options.host
    if host is None:
        # read variable from config file
        host = get_option("SERVICE:FLASK", "host")

    launch_server(debug=cl_options.debug, host=host)
