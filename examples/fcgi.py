#!/home/USER/.virtualenvs/financeager/bin/python3
"""This is an examplatory FCGI script. I use it to run financeager on uberspace.
It is assumed that financeager and the flipflop-package (interface between flask
and FCGI) are installed:
    python3 -m venv ~/.virtualenvs/financeager
    source ~/.virtualenvs/financeager/bin/activate
    pip install -U pip
    pip install financeager flipflop==1.0

The script is placed in ~/fcgi-bin and made executable. Adjust the shebang-line.

On the client side, specify the host as
    http://USER.STAR.uberspace.de/fcgi-bin/financeager.fcgi

Further reading:
https://blog.lucas-hild.de/flask-uberspace
https://gist.github.com/tocsinDE/98c423da2724d23c02ff
https://docs.python.org/3.4/howto/webservers.html
"""
import os

from flipflop import WSGIServer
from financeager.fflask import create_app

if __name__ == "__main__":
    # Configure to your liking
    app = create_app(
        data_dir=os.path.expanduser("~/.local/share/financeager"),
        # config={"DEBUG": True},
    )
    WSGIServer(app).run()
