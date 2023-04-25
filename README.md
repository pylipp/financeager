[![pypi](https://badge.fury.io/py/financeager.svg)](https://pypi.org/project/flake8-pytest-style)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://pypi.org/project/financeager)
[![Downloads](https://img.shields.io/pypi/dm/financeager.svg)](https://pypistats.org/packages/flake8-pytest-style)
![Build Status](https://github.com/pylipp/financeager/workflows/CI/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/pylipp/financeager/badge.svg?branch=master)](https://coveralls.io/github/pylipp/financeager?branch=master)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://en.wikipedia.org/wiki/GNU_General_Public_License#Version_3)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

<p align="center">
  <h1 align="center">financeager</h1>
  <p align="center">Organize your finances from the command line</p>
</p>

An application that helps you administering your daily expenses and earnings using single-entry book-keeping. Interact via the command line interface `fina`.

The `financeager` backend holds databases (internally referred to as 'pockets', stored in `~/.local/share/financeager`). A pocket contains entries for a certain project.

## Quickstart

![Quickstart](./examples/quickstart.svg)

Who is this for?
----------------
You might be someone who wants to organize finances with a simple software because you're tired of Excel and the like. And you like the command line. And Python.

## Installation

`financeager` requires Python 3.8 or higher (last version supporting Python 3.6/3.7 is 1.0.3/1.2.1).

### From PyPI package

    pip install --user --upgrade financeager

### Using pipx

If you have [`pipx`](https://pipxproject.github.io/pipx/) installed, install `financeager` into an isolated environment via

    pipx install financeager

## Usage

You can use `financeager` as a client-server or a serverless application (default). The user interacts via the command line interface (CLI).

<details>
  <summary>Click here for background information about the modes.</summary>

### Serverless mode

The user request invoked from the CLI is passed to the backend which opens the appropriate database, processes the request, closes the database and returns a response. All communication happens within a single process, hence the label 'serverless'.

In vanilla financeager, this is the default mode.

You can explicitly specify it in the configuration file `~/.config/financeager/config`  via

    [SERVICE]
    name = local

### Client-server mode

Install the [financeager-flask](https://github.com/pylipp/financeager-flask) plugin.

In any case, you're all set up! See the next section about the available client CLI commands and options.

</details>

### Command line interface

The main CLI entry point is called `fina`.

    usage: fina [-h] [-V] {add,get,remove,update,copy,list,pockets} ...

    optional arguments:
      -h, --help          show this help message and exit
      -V, --version       display version info and exit

    command
      add                 add an entry to the database
      get                 show information about single entry
      remove              remove an entry from the database
      update              update one or more fields of an entry
      copy                copy an entry from one pocket to another, or within one pocket
      list                list all entries in the pocket database
      pockets             list all pocket databases

*Add* earnings (no/positive sign) and expenses (negative sign) to the database:

    > fina add burgers -19.99 --category Restaurants
    > fina add lottery 123.45 --date 03-14

Category and date can be optionally specified. They default to None and the current day's date, resp. The program will try to derive the entry category from the database if not specified. If several matches are found, the default category is used.

> The date format can be anything that the [parser module](https://dateutil.readthedocs.io/en/stable/parser.html) of the `python-dateutil` library understands (e.g. YYYY-MM-DD, YY-MM-DD or MM-DD).

*Add recurrent* entries by specifying the frequency (yearly, half-yearly, quarterly, bi-monthly, monthly, weekly, daily) with the `-f` flag and optionally start and end date with the `-s` and `-e` flags, resp.

    > fina add rent -500 -f monthly -s 01-01 -c rent

By default, the start date is the current date. The entry exists for infinite times, i.e. the end date is evaluated as the current date at query runtime.

Did you make a mistake when adding a new entry? *Update* one or more fields by calling the `update` command with the entry's ID and the respective corrected fields:

    > fina update 1 --name "McKing Burgers" --value -18.59

To unset the end date of a recurrent entry, or the category of an entry, use a special indicator: `--end -` and `--category -`

*Remove* an entry by specifying its ID (visible in the output of the `list` command). This removes the `burgers` entry:

    > fina remove 1

This would remove the recurrent rent entries (ID is also 1 because standard and recurrent entries are stored in separate tables):

    > fina remove 1 --recurrent

Show a side-by-side *overview* of earnings and expenses (filter by date/category/name/value by passing the `--filter` option, e.g. `--filter category=food` to show entries in the categories `food`)

    > fina list

                   Earnings               |                Expenses
    Name               Value    Date  ID  | Name               Value    Date  ID
    Unspecified          123.45           | Rent                1500.00
      Lottery            123.45 03-14   2 |   Rent January       500.00 01-01   1
                                          |   Rent February      500.00 02-01   1
                                          |   Rent March         500.00 03-01   1
    =============================================================================
    Total                123.45           | Total               1500.00
    Difference         -1376.55

It might be convenient to list entries of the current month, or a specific month only (example output is omitted):

    > fina list --month
    > fina list --month January
    > fina list --month Dec
    > fina list --month 7
    > fina list --month 03

In order to only list category entries incl. their respective percentage of earnings/expenses use

    > fina list --category-percentage

In order to only list recurrent entries run (you can apply additional filtering (use `-f end=` to list entries with indefinite end) and sorting)

    > fina list --recurrent-only

The aforementioned `fina` commands operate on the default database (`main`) unless another pocket is specified by the `--pocket` flag.

    > fina add xmas-gifts -42 --date 12-23 --pocket personal

*Copy* an entry from one database to another by specifying entry ID and source/destination pocket:

    > fina copy 1 --source 2017 --destination 2018

Detailed information is available from

    > fina --help
    > fina <subcommand> --help

You can turn on printing debug messages to the terminal using the `--verbose` option, e.g.

    > fina list --verbose

You can find a log of interactions at `~/.local/share/financeager/log` (on both the client machine and the server).

### More on configuration

Besides specifying the backend to communicate with, you can also configure frontend options: the name of the default category (assigned when omitting the category option when e.g. adding an entry). The defaults are:

    [FRONTEND]
    default_category = unspecified

The CLI `fina` tries to read the configuration from `~/.config/financeager/config`. You can specify a custom path by passing it along with the `-C`/`--config` command line option.

### More Goodies

- Command line tab completion is provided by the `argcomplete` package (for bash; limited support for zsh, fish, tcsh). Completion has to be enabled by running `activate-global-python-argcomplete`. Read the [instructions](https://github.com/kislyuk/argcomplete#activating-global-completion) if you want to know more.

### Expansion

Want to use a different database? Should be straightforward by deriving from `Pocket` and implementing the `_entry()` methods. Modify the `Server` class accordingly to use the new pocket type. See also [this issue](https://github.com/pylipp/financeager/issues/18).

### Plugin support

The `financeager` core package can be extended by Python plugins.
The supported groups are:

- `financeager.services`

Available plugins are:

- [financeager-flask](https://github.com/pylipp/financeager-flask)

<details>
  <summary>Click here for instructions about creating plugins.</summary>

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

</details>

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
    |                pocket               |
    +-------------------------------------+

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

    make test

If you added a non-cosmetic change (i.e. a change in functionality, e.g. a bug fix or a new feature), please update `Changelog.md` accordingly as well. Check this README whether the content is still up to date.

## Releasing

1. Tag the latest commit on master by incrementing the current version accordingly (scheme `vmajor.minor.patch`).
1. Run `make release`.
1. The package is automatically published to PyPI using a Github action.

## Related projects

`financeager` aims to be simple in functionality. A related command-line tool is [expenses](https://github.com/manojkarthick/expenses).

For more holistic management of your financial affairs you might consider double-entry book-keeping. The following projects provide mature support:

CLI-focused (GUI/browser extensions available):
- [beancount](https://github.com/beancount/beancount)
- [ledger](https://www.ledger-cli.org/index.html)

Client-server applications
- [firefly-iii](https://www.firefly-iii.org/)

Local GUI applications
- [kmymoney](https://kmymoney.org/)
