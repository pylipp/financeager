"""Top-level service organizing databases."""
import glob
import os.path

from . import default_period_name, init_logger, period

logger = init_logger(__name__)


class Server:
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
        logger.debug("Running '{}' with {}".format(command, kwargs))

        try:
            if command == "periods":
                return {"periods": self._period_names()}
            elif command == "copy":
                return {"id": self._copy_entry(**kwargs)}
            elif command == "stop":
                # graceful shutdown, invoke closing of files
                for pd in self._periods.values():
                    pd.close()
                return {}
            else:
                period_name = kwargs.pop("period", None)
                pd = self._get_period(period_name)

                if command == "add":
                    response = {"id": pd.add_entry(**kwargs)}
                elif command == "remove":
                    response = {"id": pd.remove_entry(**kwargs)}
                elif command == "list":
                    response = {"elements": pd.get_entries(**kwargs)}
                elif command == "get":
                    response = {"element": pd.get_entry(**kwargs)}
                elif command == "update":
                    response = {"id": pd.update_entry(**kwargs)}
                else:
                    response = {
                        "error": "Server: unknown command '{}'".format(command)
                    }
                return response

        except period.PeriodException as e:
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
            pd = self._periods[name]
        except KeyError:
            logger.debug("Creating new Period '{}'".format(name))
            pd = period.TinyDbPeriod(name, **self._period_kwargs)
            self._periods[pd.name] = pd

        return pd

    def _period_names(self):
        """Return names of periods currently organized by the server.
        If persistent data storage was specified, all JSON files present in the
        'data_dir' are also taken into account.

        :return: list(str)
        """
        # Avoid duplicate entries if Period already present in self._periods by
        # using sets
        names = {p._name for p in self._periods.values()}

        data_dir = self._period_kwargs.get("data_dir")
        if data_dir is not None:
            names.update({
                os.path.splitext(os.path.basename(f))[0]
                for f in glob.glob(os.path.join(data_dir, "*.json"))
            })

        return sorted(names)

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
        return destination_period.add_entry(
            table_name=kwargs.get("table_name"), **entry_to_copy)
