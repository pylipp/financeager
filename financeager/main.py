from __future__ import unicode_literals
import argparse
from financeager.cli import Cli

def parse_command():
    parser = argparse.ArgumentParser()

    period_args = ("-p", "--period")
    period_kwargs = dict(default=None, help="name of period to modify or query")

    subparsers = parser.add_subparsers(title="subcommands", dest="command",
            help="list of available subcommands")

    add_parser = subparsers.add_parser("add",
            help="add an entry to the database")

    add_parser.add_argument("name", help="entry name")
    add_parser.add_argument("value", type=float, help="entry value")
    add_parser.add_argument("-c", "--category", default=None,
            help="entry category")
    add_parser.add_argument("-d", "--date", default=None, help="entry date")
    add_parser.add_argument(*period_args, **period_kwargs)

    stop_parser = subparsers.add_parser("stop",
            help="stop period server")
    stop_parser.add_argument(*period_args, **period_kwargs)

    rm_parser = subparsers.add_parser("rm",
            help="remove an entry from the database")
    rm_parser.add_argument("name", help="entry name")
    rm_parser.add_argument(*period_args, **period_kwargs)

    find_parser = subparsers.add_parser("find",
            help="find an entry in the database")
    find_parser.add_argument("name", help="entry name")
    find_parser.add_argument(*period_args, **period_kwargs)

    print_parser = subparsers.add_parser("print",
            help="show the period database")
    print_parser.add_argument(*period_args, **period_kwargs)

    list_parser = subparsers.add_parser("list",
            help="list all databases")
    list_parser.add_argument("-r", "--running", action='store_true',
            help="list only databases that are currently running")

    return parser.parse_args()

def main():
    args = parse_command()
    # print(vars(args))
    cli = Cli(vars(args))
    cli()

if __name__ == "__main__":
    main()
