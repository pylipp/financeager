"""Command line interface of financeager application."""

# PYTHON_ARGCOMPLETE_OK
import argparse
import os
import sys
import time
from datetime import datetime

import argcomplete
import pkg_resources
from dateutil import parser as du_parser
from rich.console import Console

import financeager

from . import (
    POCKET_DATE_FORMAT,
    RECURRENT_TABLE,
    UNSET_INDICATOR,
    __version__,
    clients,
    config,
    entries,
    exceptions,
    init_logger,
    listing,
    make_log_stream_handler_verbose,
    setup_log_file_handler,
)

logger = init_logger(__name__)

# Exit codes
SUCCESS = 0
FAILURE = 1


def main():
    """Main command line entry point of the application.

    The log directory is created. A FileHandler is added to the package logger.
    Available plugins are loaded.
    The program configuration is loaded.
    Relevant command line arguments and options are parsed and passed to
    'run()'.
    """
    os.makedirs(financeager.DATA_DIR, exist_ok=True)

    # Adding the FileHandler here avoids cluttering the log during tests
    setup_log_file_handler()

    plugins = [
        ep.load()() for ep in pkg_resources.iter_entry_points("financeager.services")
    ]

    args = _parse_command(plugins=plugins)
    try:
        configuration = config.Configuration(
            args.pop("config_filepath"), plugins=plugins
        )
        exit_code = run(configuration=configuration, plugins=plugins, **args)

    except exceptions.InvalidConfigError as e:
        logger.critical(f"Invalid configuration: {e}")
        exit_code = FAILURE

    sys.exit(exit_code)


def run(command, configuration, plugins=None, verbose=False, sinks=None, **params):
    """Run 'command' request using additional 'params'.

    All 'params' except for formatting-related options are passed to
    'Client.safely_run()'.

    'configuration' is a config.Configuration object.

    'plugins' is an optional list of plugin.PluginBase objects that is forwarded
    to respective methods (e.g. ServicePlugins to clients.create()).

    If 'verbose' is set, debug level log messages are printed to the terminal.

    'sinks' is an optional Client.Sinks object to direct program output to.
    By default, the Python built-in logging interface is used.

    :return: UNIX return code (zero for success, non-zero otherwise)
    """
    if verbose:
        make_log_stream_handler_verbose()

    formatting_options = {}

    def _info(message):
        """Wrapper to format message and propagate it to stdout. The original
        message is logged at INFO-level.
        """
        response = _format_response(message, command, **formatting_options)
        logger.info(message)

        if isinstance(response, str):
            print(response)
        else:  # pragma: no cover
            Console().print(response)

    sinks = sinks or clients.Client.Sinks(_info, logger.error)

    try:
        _preprocess(params)
    except exceptions.PreprocessingError as e:
        sinks.error(e)
        return FAILURE

    formatting_options["default_category"] = configuration.get_option(
        "FRONTEND", "default_category"
    )
    if command == "list":
        # Extract formatting options; irrelevant, even confusing for Server
        for option in [
            "stacked_layout",
            "entry_sort",
            "category_sort",
            "category_percentage",
            "json",
        ]:
            formatting_options[option] = params.pop(option)
        if params["recurrent_only"]:
            formatting_options["recurrent_only"] = True

    exit_code = FAILURE
    client = clients.create(configuration=configuration, sinks=sinks, plugins=plugins)
    if client.safely_run(command, **params):
        exit_code = SUCCESS

    client.shutdown()

    return exit_code


def _preprocess(data):
    """Preprocess data to be passed to Client (e.g. convert date format, parse
    'filters' and 'month' options passed with list command).

    :raises: PreprocessError if preprocessing failed.
    """
    for field in ["date", "start", "end"]:
        date = data.get(field)
        if field == "end" and date == UNSET_INDICATOR:
            continue  # skip validation

        if date is not None:
            try:
                date = time.strftime(
                    POCKET_DATE_FORMAT,
                    du_parser.parse(date, yearfirst=True).timetuple(),
                )
                data[field] = date
            except ValueError:
                raise exceptions.PreprocessingError("Invalid date format.")

    filter_items = data.get("filters")
    parsed_items = {}
    if filter_items is not None:
        # convert list of "key=value" strings into dictionary
        try:
            for item in filter_items:
                key, value = item.split("=")
                parsed_items[key] = value.lower()

            for field, indicator in zip(
                ["category", "end"], [entries.CategoryEntry.DEFAULT_NAME, ""]
            ):
                # Substitute category default name, or empty string for end
                try:
                    if parsed_items[field] == indicator:
                        parsed_items[field] = None
                except KeyError:
                    # No field present
                    pass

            data["filters"] = parsed_items
        except ValueError:
            # splitting returned less than two parts due to missing separator
            raise exceptions.PreprocessingError(f"Invalid filter format: {item}")

    month = data.pop("month", None)
    if month is not None:
        today = datetime.today()
        if month == "current":
            date = today

        else:
            # Attempt to convert value for 'month' option (number (zero-padded
            # or not), or month name (abbreviated or full)) to 'filters'-option.
            # This is subject to the machine's locale setting
            date = None

            # -m / #m for parsing non-zero-padded numbers on UNIX / Windows
            for fmt in ["b", "B", "m", "-m", "#m"]:
                try:
                    date = datetime.strptime(month, f"%{fmt}").replace(year=today.year)
                    break
                except ValueError:
                    continue

            if date is None:
                raise exceptions.PreprocessingError(f"Invalid month: {month}")

        if filter_items is None:
            data["filters"] = {}

        # Overwrite 'filters' setting. Filter for entries of current year
        data["filters"]["date"] = f"{date.strftime('%Y-%m')}-"

    if any([data.get(f) for f in ["frequency", "start", "end"]]):
        # Assume that entry should be added to recurrent table
        data["table_name"] = RECURRENT_TABLE
    if any(n in parsed_items for n in ["start", "end", "frequency"]):
        # Assume that only recurrent table shall be displayed
        data["recurrent_only"] = True

    for field_name in ["category", "name"]:
        field = data.get(field_name)
        if field is not None:
            field = field.strip()
            if not len(field):
                raise exceptions.PreprocessingError(f"Empty {field_name} given.")
            # Update with sanitized data field
            data[field_name] = field


def _format_response(response, command, **listing_options):
    """Format the given response (dict or str) into human-readable text.
    If the response is a string, it is immediately returned.
    If the response does not contain any of the fields 'id', 'elements',
    'element', or 'pockets', an empty string is returned.
    The 'listing_options' are passed to listing.prettify().

    :return: str
    """
    if isinstance(response, str):
        return response

    eid = response.get("id")
    if eid is not None:
        verb = {
            "add": "Added",
            "update": "Updated",
            "remove": "Removed",
            "copy": "Copied",
        }[command]
        return f"{verb} element {eid}."

    elements = response.get("elements")
    if elements is not None:
        return listing.prettify(elements, **listing_options)

    element = response.get("element")
    if element is not None:
        return entries.prettify(
            element, default_category=listing_options["default_category"]
        )

    pockets = response.get("pockets", [])
    return "\n".join([p for p in pockets])


def _parse_command(args=None, plugins=None):
    """Parse the given list of args and return the result as dict."""

    parser = argparse.ArgumentParser(
        description="An application "
        "that helps you administering your daily expenses and earnings."
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"financeager version {__version__}",
        help="display version info and exit",
    )  # pragma: no cover

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="command",
    )
    subparsers.required = True

    add_parser = subparsers.add_parser("add", help="add an entry to the database")

    add_parser.add_argument("name", help="entry name")
    add_parser.add_argument("value", type=float, help="entry value")
    add_parser.add_argument("-c", "--category", default=None, help="entry category")
    add_parser.add_argument("-d", "--date", default=None, help="entry date")

    add_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="""table to add the entry to. With 'recurrent', specify at
least a frequency, start date and end date are optional. Default:
'standard'""",
    )
    add_parser.add_argument(
        "-f",
        "--frequency",
        help="""frequency of recurrent entry; one of yearly, half-yearly,
quarterly, monthly, weekly, daily. If specified, '--table-name=recurrent'
is assumed""",
    )
    add_parser.add_argument(
        "-s", "--start", default=None, help="start date of recurrent entry"
    )
    add_parser.add_argument(
        "-e", "--end", default=None, help="end date of recurrent entry"
    )

    get_parser = subparsers.add_parser(
        "get", help="show information about single entry"
    )
    get_parser.add_argument("eid", help="entry ID")
    get_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to get the entry from. Default: 'standard'.",
    )

    remove_parser = subparsers.add_parser(
        "remove", help="remove an entry from the database"
    )
    remove_parser.add_argument("eid", help="entry ID")
    remove_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to remove the entry from. Default: 'standard'.",
    )

    update_parser = subparsers.add_parser(
        "update", help="update one or more fields of an entry"
    )
    update_parser.add_argument("eid", type=int, help="entry ID")
    update_parser.add_argument(
        "-t", "--table-name", help="Table containing the entry. Default: 'standard'"
    )
    update_parser.add_argument("-n", "--name", help="new name")
    update_parser.add_argument("-v", "--value", type=float, help="new value")
    update_parser.add_argument("-c", "--category", help="new category")
    update_parser.add_argument(
        "-d", "--date", help="new date (for standard entries only)"
    )
    update_parser.add_argument(
        "-f", "--frequency", help="new frequency (for recurrent entries only)"
    )
    update_parser.add_argument(
        "-s", "--start", help="new start date (for recurrent entries only)"
    )
    update_parser.add_argument(
        "-e", "--end", help="new end date (for recurrent entries only)"
    )

    copy_parser = subparsers.add_parser(
        "copy", help="copy an entry from one pocket to another, or within one pocket"
    )
    copy_parser.add_argument("eid", help="entry ID")
    copy_parser.add_argument(
        "-s",
        "--source",
        default=None,
        dest="source_pocket",
        help="pocket to copy the entry from (default: main pocket)",
    )
    copy_parser.add_argument(
        "-d",
        "--destination",
        default=None,
        dest="destination_pocket",
        help="pocket to copy the entry to (default: source pocket)",
    )
    copy_parser.add_argument(
        "-t",
        "--table-name",
        default=None,
        help="Table to copy the entry from/to. Default: 'standard'.",
    )

    list_parser = subparsers.add_parser(
        "list", help="list all entries in the pocket database"
    )
    list_parser.add_argument(
        "-f",
        "--filter",
        default=None,
        action="append",
        dest="filters",
        metavar="FILTER",
        help="filter for name, "
        "date and/or category substring, e.g. name=beer category=groceries. "
        "Can be specified multiple times (then filters add up)",
    )
    list_parser.add_argument(
        "-s",
        "--stacked-layout",
        action="store_true",
        help="if true, display earnings and expenses in stacked layout, "
        "otherwise side-by-side. Not effective with --recurrent-only or --json option",
    )
    list_parser.add_argument(
        "--entry-sort",
        choices=[
            "name",
            "value",
            "date",
            "eid",
            "category",
            "start",
            "end",
            "frequency",
        ],
        help="key to sort entries by. The latter four keys can only be applied "
        "in combination with the --recurrent-only option",
    )
    list_parser.add_argument(
        "--category-sort",
        choices=["name", "value"],
        help="key to sort categories by. Not effective in combination with "
        "--recurrent-only or --json option",
    )
    list_parser.add_argument(
        "-P",
        "--category-percentage",
        action="store_true",
        help="show only category entries incl. percentage. Not effective in "
        "combination with --recurrent-only or --json option",
    )
    list_parser.add_argument(
        "-m",
        "--month",
        nargs="?",
        const="current",
        help="show only entries of given month (default: current) in current year)",
    )
    list_parser.add_argument(
        "-r",
        "--recurrent-only",
        action="store_true",
        help="show only recurrent entries",
    )
    list_parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="return result in JSON format instead formatting into table. "
        "Helpful for processing data with jq or similar tools.",
    )

    subparsers.add_parser("pockets", help="list all pocket databases")

    # Extend with plugin parsers
    plugins = plugins or []
    for plugin in plugins:
        plugin.cli_options.extend(subparsers)

    # Add common options to subparsers
    for subparser in subparsers.choices.values():
        subparser.add_argument(
            "-C",
            "--config-filepath",
            default=(
                financeager.CONFIG_FILEPATH
                if os.path.exists(financeager.CONFIG_FILEPATH)
                else None
            ),
            help=f"path to config file. Default: {financeager.CONFIG_FILEPATH}",
        )
        subparser.add_argument(
            "--verbose", action="store_true", help="Be verbose about internal workings"
        )

        if subparser in [
            add_parser,
            get_parser,
            remove_parser,
            update_parser,
            list_parser,
        ]:
            subparser.add_argument(
                "-p", "--pocket", help="name of pocket to modify or query"
            )

    for subparser in [
        add_parser,
        get_parser,
        remove_parser,
        update_parser,
        copy_parser,
    ]:
        subparser.add_argument(
            "-r",
            "--recurrent",
            action="store_true",
            help="""alias for '-t recurrent'. If the -t option is simultaneously
specified, the -r option is ignored""",
        )

    argcomplete.autocomplete(parser)
    parsed_args = vars(parser.parse_args(args=args))

    # Set table name if not specified
    recurrent = parsed_args.pop("recurrent", None)
    if recurrent and parsed_args["table_name"] is None:
        parsed_args["table_name"] = RECURRENT_TABLE

    return parsed_args
