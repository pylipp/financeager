[![Coverage Status](https://coveralls.io/repos/github/pylipp/financeager/badge.svg?branch=master)](https://coveralls.io/github/pylipp/financeager?branch=master)

FINANCEAGER
===========

An application that helps you administering your daily expenses and earnings. Interact via the command line interface.

The `financeager` backend holds databases (internally referred to as 'periods'). A period contains entries of a certain year.

## Quickstart

![Quickstart](./examples/quickstart.svg)

Who is this for?
----------------
You might be someone who wants to organize finances with a simple software because you're tired of Excel and the like. And you like the command line. And Python.

NOTE
----
The project is actively developed. Expect things to break - e.g. the command line interface, the REST API definitions, ... - before version 1.0.0 is released.

## Installation

### From PyPI package

    pip install --user financeager

### Using pipx

If you're using Python >= 3.6 and have [`pipx`](https://pipxproject.github.io/pipx/) installed, install `financeager` into an isolated environment via

    pipx install financeager

## Usage

You can use `financeager` as a client-server or a serverless application (default). The user interacts via the command line interface (CLI).

### Serverless mode

The user request invoked from the CLI is passed to the backend which opens the appropriate database, processes the request, closes the database and returns a response. All communication happens within a single process, hence the label 'serverless'. The databases are stored in `~/.local/share/financeager`.

This option can be stored in the configuration file via

    [SERVICE]
    name = local

In vanilla financeager, this is little relevant since it is the default anyways.

### Client-server mode

Install the [financeager-flask](https://github.com/pylipp/financeager-flask) plugin.

In any case, you're all set up! See the next section about the available client CLI commands and options.

### Command line client

    usage: financeager [-h] [-V] {add,get,remove,update,copy,list,periods} ...

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         display version info and exit

    subcommands:
      {add,get,remove,update,copy,list,periods}
                            list of available subcommands
        add                 add an entry to the database
        get                 show information about single entry
        remove              remove an entry from the database
        update              update one or more fields of an database entry
        copy                copy an entry from one period to another
        list                list all entries in the period database
        periods             list all period databases

On the client side, `financeager` provides the following commands to interact with the backend: `add`, `update`, `remove`, `get`, `list`, `periods`, `copy`.

*Add* earnings (no/positive sign) and expenses (negative sign) to the database:

    > financeager add burgers -19.99 --category Restaurants
    > financeager add lottery 123.45 --date 03-14

Category and date can be optionally specified. They default to None and the current day's date, resp. `financeager` will try to derive the entry category from the database if not specified. If several matches are found, the default category is used.

*Add recurrent* entries using the `-t recurrent` flag (`t` for table name) and specify the frequency (yearly, half-yearly, quarterly, bi-monthly, monthly, weekly, daily) with the `-f` flag and optionally start and end date with the `-s` and `-e` flags, resp.

    > financeager add rent -500 -t recurrent -f monthly -s 01-01 -c rent

If not specified, the start date defaults to the current date and the end date to the last day of the database's year.

Did you make a mistake when adding a new entry? *Update* one or more fields by calling the `update` command with the entry's ID and the respective corrected fields:

    > financeager update 1 --name "McKing Burgers" --value -18.59

*Remove* an entry by specifying its ID (visible in the output of the `list` command). This removes the `burgers` entry:

    > financeager remove 1

This would remove the recurrent rent entries (ID is also 1 because standard and recurrent entries are stored in separate tables):

    > financeager remove 1 --table-name recurrent

Show a side-by-side *overview* of earnings and expenses (filter by date/category/name/value by passing the `--filters` option, e.g. `--filters category=food` to show entries in the categories `food`)

    > financeager list

                   Earnings               |                Expenses
    Name               Value    Date  ID  | Name               Value    Date  ID
    Unspecified          123.45           | Rent                1500.00
      Lottery            123.45 03-14   2 |   Rent January       500.00 01-01   1
                                          |   Rent February      500.00 02-01   1
                                          |   Rent March         500.00 03-01   1
    =============================================================================
    Total                123.45           | Total               1500.00
    Difference         -1376.55

It might be convenient to list entries of the current, or a specific month only (example output is omitted):

    > financeager list --month
    > financeager list --month January
    > financeager list --month Dec
    > financeager list --month 7
    > financeager list --month 03

The aforementioned `financeager` commands operate on the default database (named by the current year, e.g. 2017) unless another period is specified by the `--period` flag.

    > financeager add xmas-gifts -42 --date 12-23 --period 2016

*Copy* an entry from one database to another by specifying entry ID and source/destination period:

    > financeager copy 1 --source 2017 --destination 2018

Detailed information is available from

    > financeager --help
    > financeager <subcommand> --help

You can turn on printing debug messages to the terminal using the `--verbose` option, e.g.

    > financeager list --verbose

You can find a log of interactions at `~/.local/share/financeager/log` (on both the client machine and the server).

### More on configuration

Besides specifying the backend to communicate with, you can also configure frontend options: the name of the default category (assigned when omitting the category option when e.g. adding an entry) and the date format (string that `datetime.strptime` understands; note the double percent). The defaults are:

    [FRONTEND]
    default_category = unspecified
    date_format = %%m-%%d

The `financeager` command line client tries to read the configuration from `~/.config/financeager/config`. You can specify a custom path by passing it along with the `-C`/`--config` command line option.

### More Goodies

- Command line tab completion is provided by the `argcomplete` package (for bash; limited support for zsh, fish, tcsh). Completion has to be enabled by running `activate-global-python-argcomplete`. Read the [instructions](https://github.com/kislyuk/argcomplete#activating-global-completion) if you want to know more.

### Expansion

Want to use a different database? Should be straightforward by deriving from `Period` and implementing the `_entry()` methods. Modify the `Server` class accordingly to use the new period type.

### Plugin support

The `financeager` core package can be extended by Python plugins.
The supported groups are:

- `financeager.services`

Available plugins are:

- [financeager-flask](https://github.com/pylipp/financeager-flask)

#### All plugin types

For developing a plugin, create a plugin package containing a `main.py` file:

    from financeager import plugin

    class _Configuration(plugin.PluginConfiguration):
        """Configuration actions specific to the plugin."""

and implement the required `PluginConfiguration` methods.
Finally, specify the entry point for loading the plugin in `setup.py`:

    setup(
        ...,
        entry_points={
            <group_name>: <plugin-name> = <package>.main:main,
            # e.g.
            # "financeager.services": "fancy-service = fancy_service.main:main",
        },
    )

The plugin name can be different from the package name.
The package name should be prefixed with `financeager-`.

#### Service plugins

For developing a service plugin, extend the aforementioned `main.py` file:

    # fancy_service/main.py in the fancy-service package
    from financeager import plugin, clients

    class _Configuration(plugin.PluginConfiguration):
        """Configuration actions specific to the plugin."""

    class _Client(clients.Client):
        """Client to communicate with fancy-service."""

    def main():
        return plugin.ServicePlugin(
            name="fancy-service",
            config=_Configuration(),
            client=_Client,
        )

Provide a suitable client implementation.

Done! When the plugin is correctly installed, and configured to be used (`name = fancy-service`), `financeager` picks it up automatically. The plugin configuration is applied, and the plugin client created.

## Architecture

The following diagram sketches the relationship between financeager's modules. See the module docstrings for more information.

          +--------+
          | plugin |
          +--------+
           ¦      ¦
           V      V
    +--------+   +-----------+
    | config |-->|    cli    |
    +--------+   +-----------+

                     ¦   Λ                     +---------+     +---------+
    [pre-processing] ¦   ¦  [formatting]  <--  | listing | <-- | entries |
                     V   ¦                     +---------+     +---------+

    +-------------------------------------+
    |                clients              |
    +-------------------------------------+

            ¦                     Λ
            V                     ¦

    +-------------------------------------+
    |                                     |     FRONTEND
    |                                     |
    |            localserver              |    ==========
    |                                     |
    |                                     |     BACKEND
    +-------------------------------------+

            ¦                     Λ
            V                     ¦
    +-------------------------------------+
    |                server               |
    +-------------------------------------+
            ¦                     Λ
            V                     ¦
    +-------------------------------------+
    |                period               |
    +-------------------------------------+

## Known bugs

- see [issues](https://github.com/pylipp/financeager/labels/bug)
- Please. Report. Them.

## Contributing

Always welcome! Clone the repo

    git clone https://github.com/pylipp/financeager
    cd financeager

Create a virtual environment

    python3 -m venv .venv
    source .venv/bin/activate

Install development dependencies

    make install

You're all set for hacking!
Please adhere to test-driven development, if possible: When adding a feature, or fixing a bug, try to construct a test first, and subsequently adapt the implementation. Run the tests from the root directory via

    python setup.py test

If you added a non-cosmetic change (i.e. a change in functionality, e.g. a bug fix or a new feature), please update `Changelog.md` accordingly as well. Check this README whether the content is still up to date.

## Releasing

1. Tag the latest commit on master by incrementing the current version accordingly (scheme `v0.major.minor.patch`).
1. Run `make release`.

PERSONAL NOTE
-------------
This is a 'sandbox' project of mine. I'm exploring and experimenting with databases, data models, server applications (`Pyro4` and `flask`), frontends (command line, Qt-based GUI), software architecture, programming best practices (cough) and general Python development.

Feel free to browse the project and give feedback (comments, issues, pull requests).
