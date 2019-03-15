#!/usr/bin/env python
"""Command line interface of financeager application."""

import argparse
import os
import sys

from financeager import offline, communication, __version__,\
    init_logger, make_log_stream_handler_verbose, setup_log_file_handler
import financeager
from .entries import CategoryEntry
from .listing import Listing
from .config import Configuration
from .exceptions import PreprocessingError, InvalidRequest, CommunicationError,\
    OfflineRecoveryError, InvalidConfigError

logger = init_logger(__name__)

# Exit codes
SUCCESS = 0
FAILURE = 1


def main():
    """Main command line entry point of the application. The config and the log
    directory are created. A FileHandler is added to the package logger.
    All command line arguments and options are parsed and passed to 'run()'.
    """
    os.makedirs(financeager.DATA_DIR, exist_ok=True)

    # Adding the FileHandler here avoids cluttering the log during tests
    setup_log_file_handler()

    # Most runs return None which evaluates to return code 0
    sys.exit(run(**_parse_command()))


def run(command=None, config=None, verbose=False, **cl_kwargs):
    """High-level API entry point, useful for scripts. Run 'command' passing
    'cl_kwargs' according to what the command line interface accepts (consult
    help via `financeager [command] --help`), e.g. {"command": "add", "name":
    "champagne", "value": "99"}. All kwargs are passed to 'communication.run()'.
    'config' specifies the path to a custom config file (optional). If 'verbose'
    is set, debug level log messages are printed to the terminal.

    :return: UNIX return code (zero for success, non-zero otherwise)
    """
    if verbose:
        make_log_stream_handler_verbose()

    exit_code = FAILURE

    config_filepath = config
    if config_filepath is None and os.path.exists(financeager.CONFIG_FILEPATH):
        config_filepath = financeager.CONFIG_FILEPATH
    try:
        configuration = Configuration(filepath=config_filepath)
    except InvalidConfigError as e:
        logger.error("Invalid configuration: {}".format(e))
        return FAILURE

    backend_name = configuration.get_option("SERVICE", "name")
    communication_module = communication.module(backend_name)

    proxy_kwargs = {}
    if backend_name == "flask":
        init_logger("urllib3")
        proxy_kwargs["http_config"] = configuration.get_option("SERVICE:FLASK")
    else:  # 'none' is the only other option
        proxy_kwargs["data_dir"] = financeager.DATA_DIR

    # Indicate whether to store request offline, if failed
    store_offline = False

    proxy = communication_module.proxy(**proxy_kwargs)

    try:
        logger.info(
            communication.run(
                proxy,
                command,
                default_category=configuration.get_option(
                    "FRONTEND", "default_category"),
                date_format=configuration.get_option("FRONTEND", "date_format"),
                **cl_kwargs))
        if offline.recover(proxy):
            logger.info("Recovered offline backup.")
        exit_code = SUCCESS
    except OfflineRecoveryError:
        logger.error("Offline backup recovery failed!")
    except (PreprocessingError, InvalidRequest) as e:
        # Command is erroneous and hence not stored offline
        logger.error(e)
    except CommunicationError as e:
        logger.error(e)
        store_offline = True
    except Exception:
        logger.exception("Unexpected error")
        store_offline = True

    if store_offline and offline.add(command, **cl_kwargs):
        logger.info("Stored '{}' request in offline backup.".format(command))

    if backend_name == "none":
        communication.run(proxy, "stop")

    return exit_code


def _parse_command(args=None):
    """Parse the given list of args and return the result as dict."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="financeager version {}".format(__version__),
        help="display version info and exit")  # pragma: no cover

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
        help="list of available subcommands")

    add_parser = subparsers.add_parser(
        "add", help="add an entry to the database")

    add_parser.add_argument("name", help="entry name")
    add_parser.add_argument("value", type=float, help="entry value")
    add_parser.add_argument(
        "-c", "--category", default=None, help="entry category")
    add_parser.add_argument("-d", "--date", default=None, help="entry date")

    add_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="""table to add the entry to. With 'recurrent', specify at
least a frequency, start date and end date are optional. Default:
'standard'""")
    add_parser.add_argument(
        "-f",
        "--frequency",
        help="frequency of recurrent "
        "entry; one of yearly, half-yearly, quarterly, monthly, weekly, "
        "daily.")
    add_parser.add_argument(
        "-s", "--start", default=None, help="start date of recurrent entry")
    add_parser.add_argument(
        "-e", "--end", default=None, help="end date of recurrent entry")

    get_parser = subparsers.add_parser(
        "get", help="show information about single entry")
    get_parser.add_argument("eid", help="entry ID")
    get_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to get the entry from. Default: 'standard'.")

    rm_parser = subparsers.add_parser(
        "rm", help="remove an entry from the database")
    rm_parser.add_argument("eid", help="entry ID")
    rm_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to remove the entry from. Default: 'standard'.")

    update_parser = subparsers.add_parser(
        "update", help="update one or more fields of an database entry")
    update_parser.add_argument("eid", type=int, help="entry ID")
    update_parser.add_argument(
        "-t",
        "--table-name",
        help="Table containing the entry. Default: 'standard'")
    update_parser.add_argument("-n", "--name", help="new name")
    update_parser.add_argument("-v", "--value", type=float, help="new value")
    update_parser.add_argument("-c", "--category", help="new category")
    update_parser.add_argument(
        "-d", "--date", help="new date (for standard entries only)")
    update_parser.add_argument(
        "-f", "--frequency", help="new frequency (for recurrent entries only)")
    update_parser.add_argument(
        "-s", "--start", help="new start date (for recurrent entries only)")
    update_parser.add_argument(
        "-e", "--end", help="new end date (for recurrent entries only)")

    copy_parser = subparsers.add_parser(
        "copy", help="copy an entry from one period to another")
    copy_parser.add_argument("eid", help="entry ID")
    copy_parser.add_argument(
        "-s",
        "--source",
        default=None,
        dest="source_period",
        help="period to copy the entry from")
    copy_parser.add_argument(
        "-d",
        "--destination",
        default=None,
        dest="destination_period",
        help="period to copy the entry to")
    copy_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to copy the entry from/to. Default: 'standard'.")

    print_parser = subparsers.add_parser(
        "print", help="show the period database")
    print_parser.add_argument(
        "-f",
        "--filters",
        default=None,
        nargs="+",
        help="filter for name, "
        "date and/or category substring, e.g. name=beer category=groceries")
    print_parser.add_argument(
        "-s",
        "--stacked-layout",
        action="store_true",
        help="if true, display earnings and expenses in stacked layout, "
        "otherwise side-by-side")
    print_parser.add_argument(
        "--entry-sort",
        choices=["name", "value", "date", "eid"],
        default=CategoryEntry.BASE_ENTRY_SORT_KEY)
    print_parser.add_argument(
        "--category-sort",
        choices=["name", "value"],
        default=Listing.CATEGORY_ENTRY_SORT_KEY)

    list_parser = subparsers.add_parser("list", help="list all databases")

    # Add common options to subparsers
    for subparser in subparsers.choices.values():
        subparser.add_argument(
            "-C",
            "--config",
            help="path to config file. Default: {}".format(
                financeager.CONFIG_FILEPATH))
        subparser.add_argument(
            "--verbose",
            action="store_true",
            help="Be verbose about internal workings")

        if subparser not in [list_parser, copy_parser]:
            subparser.add_argument(
                "-p", "--period", help="name of period to modify or query")

    return vars(parser.parse_args(args=args))


if __name__ == "__main__":
    main()
