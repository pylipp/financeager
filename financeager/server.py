# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import Pyro4
from financeager.period import Period, TinyDbPeriod, PeriodException
from .config import CONFIG_DIR


class Server(object):
    """
    Server class holding the ``TinyDbPeriod`` databases.

    All database handling is taken care of in the underlying `TinyDbPeriod`.
    Kwargs (f.i. storage) are passed to the TinyDbPeriod member.
    """

    def __init__(self, **kwargs):
        self._periods = {}
        self._period_kwargs = kwargs

    def run(self, command, **kwargs):
        """
        The requested period is created if not yet present. The method of
        `Period` corresponding to the given `command` is called. All `kwargs`
        are passed on. A json-like response is returned.
        
        :return: dict
            key is one of 'id', 'element', 'elements', 'error'
        """

        if command == "list":
            return self.periods(running=kwargs.get("running", False))
        elif command == "stop":
            # graceful shutdown, invoke closing of files
            for period in self._periods.values():
                period.close()
        else:
            period_name = kwargs.pop("period", None)
            if period_name not in self._periods:
                # default period stored with key 'None'
                self._periods[period_name] = TinyDbPeriod(period_name,
                        **self._period_kwargs)

            period = self._periods[period_name]

            try:
                if command == "add":
                    response = {"id": period.add_entry(**kwargs)}
                elif command == "rm":
                    response = {"id": period.remove_entry(**kwargs)}
                elif command == "print":
                    response = {"elements": period.get_entries(**kwargs)}
                elif command == "get":
                    response = {"element": period.get_entry(**kwargs)}
                elif command == "update":
                    response = {"id": period.update_entry(**kwargs)}
                else:
                    response = {"error": "Server: unknown command '{}'".format(command)}
            except PeriodException as e:
                response = {"error": str(e)}

            return response

    def periods(self, running=False):
        if running:
            return {"periods": [p._name for p in self._periods.values()]}
        else:
            filenames = []
            for file in os.listdir(CONFIG_DIR):
                filename, extension = os.path.splitext(file)
                if extension in [".json"]:
                    filenames.append(filename)
            return {"periods": filenames}


@Pyro4.expose
class PyroServer(Server):
    """
    Communicated with via Pyro.

    The server is typically launched at the initial `financeager`
    command line call and then runs in the background as a Pyro daemon.
    """

    NAME = "financeager_tinydb_server"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._running = True

    @property
    def running(self):
        return self._running

    def run(self, command, **kwargs):
        """Cause the Pyro Daemon request loop to stop if requested, then call
        parent method.
        """

        if command == "stop":
            self._running = False

        return super().run(command, **kwargs)


def launch_server():
    print("'start' command has no effect with SERVICE.name configured as 'none'.")


class LocalServer(Server):
    """Subclass mocking a locally running server that shuts down (i.e. closes
    opened files) right after running a command.
    """

    def run(self, command, **kwargs):
        response = super().run(command, **kwargs)

        if command != "stop":
            # don't shutdown twice
            super().run("stop")

        return response


def proxy():
    return LocalServer()


CommunicationError = Exception
