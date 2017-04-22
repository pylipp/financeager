# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import Pyro4
from financeager.period import Period, TinyDbPeriod, CONFIG_DIR


class Server(object):
    """
    Server class holding the ``TinyDbPeriod`` databases.

    All database handling is taken care of in the underlying `TinyDbPeriod`.
    Kwargs (f.i. storage) are passed to the TinyDbPeriod member.
    """

    def __init__(self, **kwargs):
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self._periods = {}
        self._period_kwargs = kwargs

    def run(self, command, **kwargs):
        """
        The requested period is created if not yet present. The method of
        `Period` corresponding to the given `command` is
        looked up and called. All `kwargs` are passed on. The return value
        (type: dictionary, serializable by Pyro) can later be used to access
        possible output data from querying commands (f.i. `print`).
        """

        if command == "list":
            return self.periods()
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

            command2method = {
                    "add": "add_entry",
                    "rm": "remove_entry",
                    "print": "print_entries"
                    }
            response = getattr(
                    self._periods[period_name], command2method[command])(**kwargs)
            return response

    def periods(self):
        return {"periods": [p._name for p in self._periods.values()]}

@Pyro4.expose
class PyroServer(Server):
    """
    Communicated with via Pyro.

    The server is typically launched at the initial `financeager`
    command line call and then runs in the background as a Pyro daemon.
    Calling `stop` causes the Pyro daemon request loop to terminate.
    """

    NAME = "financeager_tinydb_server"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._running = True

    @property
    def running(self):
        return self._running

    def run(self, command, **kwargs):
        if command == "stop":
            self._running = False

        return super().run(command, **kwargs)
