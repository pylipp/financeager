"""Top-level service organizing databases."""

import glob
import os.path

from . import DEFAULT_POCKET_NAME, exceptions, init_logger, pocket

logger = init_logger(__name__)


class Server:
    """Server class holding the ``TinyDbPocket`` databases.

    All database handling is taken care of in the underlying `TinyDbPocket`.
    Kwargs (f.i. storage) are passed to the TinyDbPocket member.
    """

    def __init__(self, **kwargs):
        self._pockets = {}
        self._pocket_kwargs = kwargs

    def run(self, command, **kwargs):
        """The requested pocket is created if not yet present. The method of
        `Pocket` corresponding to the given `command` is called. All `kwargs`
        are passed on. A json-like response is returned.

        Wrap this in a 'broad' try-except block to catch any server-side errors.
        :return: dict
            key is one of 'id', 'element', 'elements', 'error', 'pockets'
        """
        logger.debug(f"Running '{command}' with {kwargs}")

        try:
            if command == "pockets":
                return {"pockets": self._pocket_names()}
            elif command == "copy":
                return {"id": self._copy_entry(**kwargs)}
            elif command == "stop":
                # graceful shutdown, invoke closing of files
                for pd in self._pockets.values():
                    pd.close()
                return {}
            else:
                pocket_name = kwargs.pop("pocket", None)
                pd = self._get_pocket(pocket_name)

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
                    response = {"error": f"Server: unknown command '{command}'"}
                return response

        except exceptions.PocketException as e:
            return {"error": e}

    def _get_pocket(self, name=None):
        """Get the Pocket identified by 'name' from the Pockets dictionary. If
        the Pocket does not exist, it is created and returned. If 'name' is
        None, the default pocket name is used as defined in __init__.py

        :type name: str or None
        :return: Pocket object
        """
        name = name or DEFAULT_POCKET_NAME
        try:
            pd = self._pockets[name]
        except KeyError:
            logger.debug(f"Loading pocket '{name}'")
            pd = pocket.TinyDbPocket(name, **self._pocket_kwargs)
            self._pockets[pd.name] = pd

        return pd

    def _pocket_names(self):
        """Return names of pockets currently organized by the server.
        If persistent data storage was specified, all JSON files present in the
        'data_dir' are also taken into account.

        :return: list(str)
        """
        # Avoid duplicate entries if Pocket already present in self._pockets by
        # using sets
        names = {p._name for p in self._pockets.values()}

        data_dir = self._pocket_kwargs.get("data_dir")
        if data_dir is not None:
            names.update(
                {
                    os.path.splitext(os.path.basename(f))[0]
                    for f in glob.glob(os.path.join(data_dir, "*.json"))
                }
            )

        return sorted(names)

    def _copy_entry(self, source_pocket=None, destination_pocket=None, **kwargs):
        """Copy an entry (specified by ID and table_name) from the source pocket
        to the destination pocket.

        :type _pocket: str
        :return: ID of copied entry
        :raises: PocketException if the source entry does not exist
        """
        source_pocket = self._get_pocket(source_pocket)
        entry_to_copy = source_pocket.get_entry(**kwargs)

        destination_pocket = self._get_pocket(destination_pocket)
        return destination_pocket.add_entry(
            table_name=kwargs.get("table_name"), **entry_to_copy
        )
