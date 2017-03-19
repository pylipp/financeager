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
You're currently on the `cli` branch which is under active development.
The code base is being refactored. The idea is to first have a command line
tool and successively built a GUI on top.

GENERAL USAGE
-------------
### Installation
Create a virtual environment

    mkvirtualenv --python=/usr/lib/python2.7 financeager

Clone the repo, checkout branch `cli`

    git clone https://github.com/pylipp/financeager.git
    git checkout -b cli cli

Install via pip

    pip install -r requirements.txt -e .

Regarding the `PyQt4` dependency, I cheated by creating links to the packages
that came with my installation of git-cola.

    ln -s /usr/lib/python3/dist-packages/PyQt5 ~/.virtualenvs/financeager/lib/python3.5/site-packages/PyQt5
    ln -s /usr/lib/python2.7/dist-packages/sip.x86_64-linux-gnu.so ~/.virtualenvs/financeager/lib/python2.7/site-packages/sip.x86_64-linux-gnu.so

### Testing
The command line functionality is not fully implemented yet. However, you're
invited to run the tests from the root directory:

    python -m unittest discover

KNOWN BUGS
----------
- Report. Them.

FUTURE FEATURES
---------------
