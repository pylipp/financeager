FINANCEAGER
===========

A PyQt application that helps you administering your daily expenses and receipts.

Who is this for?
----------------
You might be someone who wants to organize finances with a simple software
because you're tired of Excel and the like.
Or you are interested in PyQt applications and like to see some example code.

DISCLAIMER: Defs not BUG-FREE!

NOTE
----
You're currently on the `master` branch which is under active development.
The code base is being refactored. The idea is to first have a command line
tool and successively built a GUI on top.

GENERAL USAGE
-------------
### Installation

Install the dependencies (I'm on Ubuntu Xenial):

    sudo apt-get install python3-pyqt5

Create a virtual environment

    mkvirtualenv --python=/usr/bin/python3 financeager

Create links for the virtual environment to find PyQt5 (same for `sip` library)

    ln -s /usr/lib/python3/dist-packages/PyQt5 $WORKON_HOME/financeager/lib/python3.5/site-packages/PyQt5

Clone the repo

    git clone https://github.com/pylipp/financeager.git

Install (uses pip)

    make install

### Testing

You're invited to run the tests from the root directory:

    make test

### Client-server or serverless mode?

You can run `financeager` as a client-server or a serverless application (default).

In the first case, specify `SERVICE.name = flask` in the config file at `~/.config/financeager`.

Launch the server via

    > financeager start

Host IP and debug mode are read from the configuration. Personally I run a financeager server on my Raspi, making it accessible via local network by setting `host=0.0.0.0`.

On the client side, specify the host in the config (defaults to localhost, so rather put the server IP).

### Command line usage

Add earnings (no/positive sign) and expenses (negative sign) to the database:

    > financeager add burgers -19.99 --category Restaurants
    > financeager add lottery 123.45 --date 2017-03-14

Category and date can be optionally specified. They default to None and the current day's date, resp. `financeager` will try to derive the entry category from the database if not specified. If several matches are found, the default category is used.

Add repetitive entries using the `-r FREQUENCY [START END]` flag.

    > financeager add rent -500 -r monthly 2017-01-01 -c rent

If not specified, the start date defaults to the current date and the end date to the last day of the database's year.

Remove an entry by

    > financeager rm burgers

Nothing is removed if the query gives multiple or no results.

Show a side-by-side overview of earnings and expenses (filter date and/or category by providing the `-d` and `-c` flag and/or filter the name by providing a positional argument)

    > financeager print

                   Earnings                |                Expenses
	Name               Value    Date       | Name               Value    Date
	Unspecified          123.45            | Rent                1500.00
	  Lottery            123.45 2017-03-14 |   Rent January       500.00 2017-01-01
	                                       |   Rent February      500.00 2017-02-01
					       |   Rent March         500.00 2017-03-01
	===============================================================================
	Total                123.45            | Total               1500.00

All financeager command operate on the default database (named by the current year, e.g. 2017) unless another period is specified by the `--period` flag.

	> financeager add xmas-gifts -42 --date 2016-12-23 --period 2016

Detailed information is available from

	> financeager --help
	> financeager <subcommand> --help

KNOWN BUGS
----------
- Please. Report. Them.

FUTURE FEATURES
---------------
- [ ] select from multiple options if possible (e.g. when searching or deleting an entry)
- [x] repetitive entries
- [x] refactor TinyDbPeriod (return Model strings)
- [x] stacked layout for `print`
- [x] detect category from entry name
- [x] display entries of single month
- [x] improve documentation (period module)
- [ ] create Python package
- [ ] set up Travis CI
- [x] use flask for REST API
- [ ] use asynchronous calls
- [ ] use logging module instead of print
- [ ] omit year with `-d` option
- [ ] drop PyQt dependency for schematics package

PERSONAL NOTE
-------------
This is a 'sandbox' project of mine. I'm exploring and experimenting with databases, server applications (`Pyro4` and `flask`), frontends (command line, Qt-based GUI), software architecture and general Python development.

Feel free to browse the project and give feedback (comments, issues, PRs).
