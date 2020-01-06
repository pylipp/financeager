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

The uberspace domain is publicly accessible. For basic authentication, run
    htpasswd -m -c /var/www/virtual/USER/.htuser USER

and add a file ~/fcgi-bin/.htaccess with content
    AuthType Basic
    AuthName flask-financeager
    AuthUserFile /var/www/virtual/USER/.htuser
    Require valid-user

On the client side, specify user and password in the config file as documented
in the main README.

You can prettify the URL format by adding a file ~/html/.htaccess with content
    RewriteEngine On
    RewriteRule ^financeager/(.*)$ /fcgi-bin/financeager.fcgi/$1 [QSA,L]

Force a restart of the FCGI app by killing the existing one.
This allows you to access via
    http://USER.STAR.uberspace.de/financeager

Further reading:
https://blog.lucas-hild.de/flask-uberspace
https://gist.github.com/tocsinDE/98c423da2724d23c02ff
https://docs.python.org/3.4/howto/webservers.html
https://wiki.uberspace.de/webserver:htaccess#verzeichnisschutz
"""
from flipflop import WSGIServer

from financeager import DATA_DIR, fflask

if __name__ == "__main__":
    # Configure to your liking
    app = fflask.create_app(
        data_dir=DATA_DIR,
        # config={"DEBUG": True},
    )
    WSGIServer(app).run()
