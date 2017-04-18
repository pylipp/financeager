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

Create links for the virtual environment to find PyQt5

    ln -s /usr/lib/python3/dist-packages/PyQt5 $WORKON_HOME/financeager/lib/python3.5/site-packages/PyQt5

Clone the repo, the branch `cli_py3` is checked out by default

    git clone https://github.com/pylipp/financeager.git

Install (uses pip)

    make install

### Testing
You're invited to run the tests from the root directory:

    make test

### Command line usage

Add earnings (no/positive sign) and expenses (negative sign) to the database:

    > financeager add burgers -19.99 --category Restaurants
    > financeager add lottery 123.45 --date 2017-03-14

Category and date can be optionally specified. They default to None and the current day's date, resp. `financeager` will try to derive the entry category from the database if not specified. If several matches are found, the default category is used. 

Add repetitive entries using the `-r FREQUENCY [START END]` flag.

    > financeager add rent -500 -r monthly 2017-01-01 -c rent

If not specified, the start date defaults to the current date and the end date to the last day of the database's year.

Remove an entry by (removes the first entry found)

    > financeager rm burgers

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
- [ ] improve documentation (period module)
- [ ] create Python package
- [ ] set up Travis CI
- [ ] use flask for REST API
