from __future__ import unicode_literals

import traceback

from financeager.period import Period, TinyDbPeriod, PeriodException


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

        # broad exception block to always have info returned to client
        try:
            if command == "list":
                return {"periods": [p._name for p in self._periods.values()]}
            elif command == "stop":
                # graceful shutdown, invoke closing of files
                for period in self._periods.values():
                    period.close()
            else:
                period_name = kwargs.pop("period", None)
                period = self._get_period(period_name)

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

        except Exception:
            return {"error": traceback.format_exc()}

    def _get_period(self, name):
        """Get the Period identified by 'name' from the Periods dictionary. If
        the Period does not exist, it is created and returned. If 'name' is
        None, 'Period.DEFAULT_NAME' is used.

        :type name: str or None
        :return: Period object
        """
        name = name or str(Period.DEFAULT_NAME)
        try:
            period = self._periods[name]
        except KeyError:
            period = TinyDbPeriod(name, **self._period_kwargs)
            self._periods[period.name] = period

        return period


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


def proxy(**kwargs):
    return LocalServer(**kwargs)


CommunicationError = Exception
