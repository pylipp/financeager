[![Build Status](https://travis-ci.org/pylipp/financeager.svg?branch=master)](https://travis-ci.org/pylipp/financeager)
[![Coverage Status](https://coveralls.io/repos/github/pylipp/financeager/badge.svg?branch=master)](https://coveralls.io/github/pylipp/financeager?branch=master)

FINANCEAGER
===========

An application (possibly running as Flask webservice) that helps you administering your daily expenses and earnings. Interact via the command line interface.

The `financeager` backend holds databases (internally referred to as 'periods'). A period contains entries of a certain year.

Who is this for?
----------------
You might be someone who wants to organize finances with a simple software because you're tired of Excel and the like. And you like the command line. And Python.

NOTE
----
You're currently on the `master` branch which is under active development.

## Installation

### From PyPI package

    pip install financeager

### From source (master branch)

Clone the repo

    git clone https://github.com/pylipp/financeager
    cd financeager

Create a virtual environment

    python -m virtualenv --python=$(which python3) .venv
    source .venv/bin/activate

Install

    pip install --upgrade --editable .

Alternatively, you can omit the second and third step and install `financeager` to `~/.local` with (requires `pip3`)

    pip3 install . --user

## Testing

You're invited to run the tests from the root directory:

    git clone https://github.com/pylipp/financeager
    cd financeager
    python setup.py test

## Usage

You can use `financeager` as a client-server or a serverless application (default). The user interacts via the command line interface (CLI).

### Serverless mode

The user request invoked from the CLI is passed to the backend which opens the appropriate database, processes the request, closes the database and returns a response. All communication happens within a single process, hence the label 'serverless'. The databases are stored in `~/.local/share/financeager`.

### Client-server mode

To run `financeager` as client-server application, start the flask webservice by

    export FLASK_APP=financeager/fflask.py
    flask run  # --help for more info

>   This does not store data persistently! Specify the environment variable `FINANCEAGER_DATA_DIR`.

>   For production use, you should wrap `app = fflask.create_app(data_dir=...)` in a WSGI.

To communicate with the webservice, the `financeager` configuration has to be adjusted. Create and open the file `~/.config/financeager/config`. If you're on the machine that runs the webservice, put the lines

    [SERVICE]
    name = flask

If you're on an actual remote 'client' machine, put

    [SERVICE]
    name = flask

    [SERVICE:FLASK]
    host = https://foo.pythonanywhere.com
    timeout = 10
    username = foouser
    password = S3cr3t

This specifies the timeout for HTTP requests and username/password for basic auth, if required by the server.

In any case, you're all set up! See the next section about the available client CLI commands and options.

### Command line client

    usage: financeager [-h] {add,get,rm,update,copy,print,list} ...

    optional arguments:
      -h, --help            show this help message and exit
      -V, --version         display version info and exit

    subcommands:
      {add,get,rm,update,copy,print,list}
                            list of available subcommands
        add                 add an entry to the database
        get                 show information about single entry
        rm                  remove an entry from the database
        update              update one or more fields of an database entry
        copy                copy an entry from one period to another
        print               show the period database
        list                list all databases

On the client side, `financeager` provides the following commands to interact with the backend: `add`, `update`, `rm`, `get`, `print`, `list`, `copy`.

*Add* earnings (no/positive sign) and expenses (negative sign) to the database:

    > financeager add burgers -19.99 --category Restaurants
    > financeager add lottery 123.45 --date 03-14

Category and date can be optionally specified. They default to None and the current day's date, resp. `financeager` will try to derive the entry category from the database if not specified. If several matches are found, the default category is used.

*Add recurrent* entries using the `-t recurrent` flag (`t` for table name) and specify the frequency (yearly, half-yearly, quarterly, bi-monthly, monthly, weekly, daily) with the `-f` flag and optionally start and end date with the `-s` and `-e` flags, resp.

    > financeager add rent -500 -t recurrent -f monthly -s 01-01 -c rent

If not specified, the start date defaults to the current date and the end date to the last day of the database's year.

Did you make a mistake when adding a new entry? *Update* one or more fields by calling the 'update' command with the entry's ID and the respective corrected fields:

    > financeager update 1 --name "McKing Burgers" --value -18.59

*Remove* an entry by specifying its ID (visible in the output of the `print` command). This removes the `burgers` entry:

    > financeager rm 1

This would remove the recurrent rent entries (ID is also 1 because standard and recurrent entries are stored in separate tables):

    > financeager rm 1 --table-name recurrent

Show a side-by-side *overview* of earnings and expenses (filter by date/category/name/value by passing the `--filters` option, e.g. `--filters category=food` to show entries in the categories `food`)

    > financeager print

                   Earnings               |                Expenses
    Name               Value    Date  ID  | Name               Value    Date  ID
    Unspecified          123.45           | Rent                1500.00
      Lottery            123.45 03-14   2 |   Rent January       500.00 01-01   1
                                          |   Rent February      500.00 02-01   1
                                          |   Rent March         500.00 03-01   1
    =============================================================================
    Total                123.45           | Total               1500.00

The aforementioned `financeager` commands operate on the default database (named by the current year, e.g. 2017) unless another period is specified by the `--period` flag.

    > financeager add xmas-gifts -42 --date 12-23 --period 2016

*Copy* an entry from one database to another by specifying entry ID and source/destination period:

    > financeager copy 1 --source 2017 --destination 2018

Detailed information is available from

    > financeager --help
    > financeager <subcommand> --help

You can turn on printing debug messages to the terminal using the `--verbose` option, e.g.

    > financeager print --verbose

You can find a log of interactions at `~/.local/share/financeager/log`.

### More on configuration

Besides specifying the backend to communicate with, you can also configure frontend options: the name of the default category (assigned when omitting the category option when e.g. adding an entry) and the date format (string that `datetime.strptime` understands; note the double percent). The defaults are:

    [FRONTEND]
    default_category = unspecified
    date_format = %%m-%%d

The `financeager` command line client tries to read the configuration from `~/.config/financeager/config`. You can specify a custom path by passing it along with the `-C`/`--config` command line option.

### More Goodies

- `financeager` will store requests if the server is not reachable (the timeout is configurable). The offline backup is restored the next time a connection is established. This feature is only available when running financeager with flask.

### Expansion

Want to use a different database? Should be straightforward by deriving from `Period` and implementing the `_entry()` methods. Modify the `Server` class accordingly to use the new period type.

## Architecture

The following diagram sketches the relationship between financeager's modules. See the module docstrings for more information.

    +--------+   +-----------+   +---------+
    | config |-->|    cli    |<->| offline |
    +--------+   +-----------+   +---------+
                     ¦   Λ
                     V   ¦
    +-------------------------------------+
    |             communication           |
    +-------------------------------------+
                                               +---------+     +---------+
      [pre-processing]      [formatting]  <--  | listing | <-- | entries |
                                               +---------+     +---------+
            ¦                     Λ
            V                     ¦

    +--------------+   |   +--------------+
    | httprequests |   |   |              |     FRONTEND
    +--------------+   |   |              |
    ================   |   |              |    ==========
    +--------------+   |   | localserver  |
    |    fflask    |   |   |              |     BACKEND
    +--------------+   |   |              |
    |  resources   |   |   |              |
    +--------------+   |   +--------------+

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

- see [issues](https://github.com/pylipp/financeager/issues)
- Please. Report. Them.

## `financeager` features

### Future features

- [ ] experiment with urwid for building TUI or remi for HTML-based GUI
- [ ] support querying of standard/recurrent table with `print`
- [x] return element data as response to add/copy/update request
- [ ] support passing multiple elements IDs to update/rm/copy/get (maybe together with asynchronous HTTP requests)
- [ ] extended period names (something along `2018-personal`)
- [ ] support `print` at date other than today

### Implemented features

- [x] recurrent entries
- [x] stacked layout for `print`
- [x] detect category from entry name (category cache)
- [x] allow filtering of specific date, name, etc. for `print`
- [x] use flask for REST API
- [x] always show entry ID when `print`ing
- [x] specify date format as `MM-DD`
- [x] validate user input prior to inserting to database
- [x] support `get` command
- [x] support 'updating' of entries
- [x] sort `print` output acc. to entry name/value/date/category
- [x] refactor config module (custom method to intuitively retrieve config parameters)
- [x] `copy` command to transfer recurrent entries between period databases
- [x] support specifying custom flask host/config with all cli commands

### Discarded feature ideas

- select from multiple options if possible (e.g. when searching or deleting an entry): breaks the concept of having a single request-response action. Instead, the user is expected to know which element he wants to delete (by using the element ID) and can give a precise command

## Developer's TODOs

- [x] refactor TinyDbPeriod (return Model strings)
- [x] improve documentation (period module)
- [x] create Python package
- [x] set up Travis CI
- [x] drop PyQt dependency for schematics package
- [x] allow remove elements by ID only
- [x] specify CL option to differ between removing standard and recurrent element
- [x] refactor `entries` module (no dependency on schematics package)
- [x] consistent naming (recurrent instead of repetitive)
- [x] increase code coverage
- [x] refactor period module (no use of CONFIG_DIR)
- [x] refactor some modules (e.g. split fflask and server)

## Roadmap for release of version 1.0

This requires some restructuring of the software architecture. Motivation and goals are outlined below.

### Status quo

- module functionalities and responsibilities particularly overlap
- also apparent in test code: no clear distinction between integration and unit tests

### Goals

- three separated top modules: core, backend, client
- responsibilities:
    1. core:
        - constants
        - configuration (maybe move to client)
        - exceptions
    2. backend:
        - interfaces (localserver, fflask)
        - REST API (resources)
        - database management (server, period)
    3. client
        - CLI
        - communication pre-/post-processing
        - HTTP requests
        - response formatting (entries, listing)
- consistent, modular test structure
- pave way for terminal user interface

### TODOs

- [x] remove TinyDB usage from model and entries
- [x] remove entries import from period
- [ ]  more fine-grained error-handling in period (distinguish between errors during validation and about non-existing elements)
- [x] integration test of cli module
- [x] move data dir to ~/.local/share/financeager
- [ ] install pre-commit framework
- [x] use logging module instead of print
- [ ] use marshmallow package for keyword validation/serialization in period and resources
- [x] have return codes in cli.run
- [x] introduce `verbose` cli option
- [x] add loggers to config and offline modules
- [x] add loggers to resources and server
- [x] avoid test code interfering with actual file system content
- [x] test offline feature with 'none' backend
- [x] rename 'model' to 'listing'
- [x] clean up `test_communication`

PERSONAL NOTE
-------------
This is a 'sandbox' project of mine. I'm exploring and experimenting with databases, data models, server applications (`Pyro4` and `flask`), frontends (command line, Qt-based GUI), software architecture, programming best practices (cough) and general Python development.

Feel free to browse the project and give feedback (comments, issues, pull requests).
