"""Top-level backend organization of databases."""

from __future__ import unicode_literals

from . import default_period_name
from .period import TinyDbPeriod, PeriodException


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

        Wrap this in a 'broad' try-except block to catch any server-side errors.
        :return: dict
            key is one of 'id', 'element', 'elements', 'error', 'periods'
        """
        try:
            if command == "list":
                return {"periods": [p._name for p in self._periods.values()]}
            elif command == "copy":
                return {"id": self._copy_entry(**kwargs)}
            elif command == "stop":
                # graceful shutdown, invoke closing of files
                for period in self._periods.values():
                    period.close()
            else:
                period_name = kwargs.pop("period", None)
                period = self._get_period(period_name)

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
                return response

        except PeriodException as e:
            return {"error": str(e)}

    def _get_period(self, name=None):
        """Get the Period identified by 'name' from the Periods dictionary. If
        the Period does not exist, it is created and returned. If 'name' is
        None, the default period name is used as defined in __init__.py

        :type name: str or None
        :return: Period object
        """
        name = name or default_period_name()
        try:
            period = self._periods[name]
        except KeyError:
            period = TinyDbPeriod(name, **self._period_kwargs)
            self._periods[period.name] = period

        return period

    def _copy_entry(self, source_period=None, destination_period=None,
                    **kwargs):
        """Copy an entry (specified by ID and table_name) from the source period
        to the destination period.

        :type _period: str
        :return: ID of copied entry
        :raises: PeriodException if the source entry does not exist
        """
        source_period = self._get_period(source_period)
        entry_to_copy = source_period.get_entry(**kwargs)

        destination_period = self._get_period(destination_period)
        return destination_period.add_entry(table_name=kwargs.get("table_name"),
                                            **entry_to_copy)
