#!/usr/bin/env python

from financeager.config import CONFIG
from financeager.fflask import create_app


if __name__ == "__main__":
    try:
        app = create_app()
        app.run(
                debug=CONFIG["SERVICE:FLASK"].getboolean("debug"),
                host=CONFIG["SERVICE:FLASK"]["host"]
                )
    except OSError as e:
        # socket binding: address already in use
        print("The financeager server has already been started.")
