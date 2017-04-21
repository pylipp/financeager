# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
from abc import ABCMeta, abstractmethod
import Pyro4
from financeager.period import Period, TinyDbPeriod, CONFIG_DIR


class Server(object):
    """
    Abstract class holding the databases. Communicated with via Pyro.

    The server is typically launched at the initial `financeager`
    command line call and then runs in the background as a Pyro daemon.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self._running = True
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self._periods = {}

    @property
    def running(self):
        return self._running

    @abstractmethod
    def run(self, command, **kwargs):
        """The method of `Period` corresponding to the given `command` is
        looked up and called. All `kwargs` are passed on. The return value
        (type: dictionary, serializable by Pyor) can later be used to access
        possible output data from querying commands (f.i. `print`).
        Calling `stop` causes the Pyro daemon request loop to terminate.
        """
        if command == "stop":
            self._running = False
        else:
            command2method = {
                    "add": "add_entry",
                    "rm": "remove_entry",
                    "print": "print_entries"
                    }
            period_name = kwargs.pop("period", str(Period.DEFAULT_NAME))
            response = getattr(
                    self._periods[period_name], command2method[command])(**kwargs)
            return response

@Pyro4.expose
class TinyDbServer(Server):
    """
    Server implementation holding `TinyDbPeriod` databases.

    All database handling is taken care of in the underlying `TinyDbPeriod`.
    Kwargs (f.i. storage) are passed to the TinyDbPeriod member.
    """

    NAME = "financeager_tinydb_server"

    def __init__(self, **kwargs):
        super(TinyDbServer, self).__init__()
        self._period_kwargs = kwargs

    def run(self, command, **kwargs):
        """
        Create the requested TinyDbPeriod if not yet present, then run the
        command.
        """

        if command == "stop":
            # graceful shutdown, invoke closing of files
            for period in self._periods.values():
                period.close()
        else:
            period_name = kwargs.get("period")
            if period_name not in self._periods:
                # default period stored with key 'None'
                self._periods[period_name] = TinyDbPeriod(period_name,
                        **self._period_kwargs)

        return super(TinyDbServer, self).run(command, **kwargs)
