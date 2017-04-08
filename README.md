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
You're currently on the `cli_py3` branch which is under active development.
The code base is being refactored. The idea is to first have a command line
tool and successively built a GUI on top.

GENERAL USAGE
-------------
### Installation
Install the dependencies (I'm on Ubuntu Trusty):

    sudo apt-get install python3-pyqt5

Create a virtual environment

    mkvirtualenv --python=/usr/bin/python3 financeager

Create links for the virtual environment to find PyQt5

    ln -s /usr/lib/python3/dist-packages/PyQt5 ~/.virtualenvs/financeager/lib/python3.5/site-packages/PyQt5

Clone the repo, the branch `cli_py3` is checked out by default

    git clone https://github.com/pylipp/financeager.git

Install (uses pip)

    make install

### Testing
You're invited to run the tests from the root directory:

    make test

KNOWN BUGS
----------
- Report. Them.

FUTURE FEATURES
---------------
- [ ] select from multiple options if possible (e.g. when searching or deleting an entry)
- [x] repetitive entries
- [ ] refactor TinyDbPeriod (return Model strings)
- [x] stacked layout for `print`
- [x] detect category from entry name
- [x] display entries of single month
- [ ] create Python package
- [ ] set up Travis CI
