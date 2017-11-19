from __future__ import unicode_literals

from financeager.period import TinyDbPeriod, PeriodException


class Server(object):
    """Server class holding the ``TinyDbPeriod`` databases.

    All database handling is taken care of in the underlying `TinyDbPeriod`.
    Kwargs (f.i. storage) are passed to the TinyDbPeriod member.
    """

    def __init__(self, **kwargs):
        self._periods = {}
        self._period_kwargs = kwargs

    def run(self, command, **kwargs):
        """The requested period is created if not yet present. The method of
        `Period` corresponding to the given `command` is called. All `kwargs`
        are passed on. A json-like response is returned.

        :return: dict
            key is one of 'id', 'element', 'elements', 'error', 'periods'
        """

        if command == "list":
            return {"periods": [p._name for p in self._periods.values()]}
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
                    response = {"error":
                                "Server: unknown command '{}'".format(command)}
            except PeriodException as e:
                response = {"error": str(e)}

            return response


def launch_server(**kwargs):
    print(
        "'start' command has no effect with SERVICE.name configured as 'none'.")


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
