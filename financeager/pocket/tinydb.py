import os.path

from tinydb import Query, TinyDB, storages

from .. import DEFAULT_TABLE
from .base import Pocket
from .utils import DatabaseInterface


class TinyDbInterface(DatabaseInterface):
    """Database interface implementation using TinyDB."""

    def __init__(self, *args, **kwargs):
        """Initialize TinyDB instance.

        :param args: positional arguments for TinyDB constructor
        :param kwargs: keyword arguments for TinyDB constructor
        """
        self._db = TinyDB(*args, **kwargs)

    def retrieve(self, table_name, condition=None):
        if condition is None:
            elements = self._db.table(table_name).all()
        else:
            elements = self._db.table(table_name).search(condition)
        # Flatten tinydb Documents into dict
        return [{**e, **{"eid": e.doc_id}} for e in elements]

    def retrieve_by_id(self, table_name, element_id):
        result = self._db.table(table_name).get(doc_id=int(element_id))
        if result is None:
            return
        return dict(result)  # convert tinydb.Document

    def create(self, table_name, data):
        return self._db.table(table_name).insert(data)

    def update_by_id(self, table_name, element_id, data):
        return self._db.table(table_name).update(data, doc_ids=[int(element_id)])[0]

    def delete_by_id(self, table_name, element_id):
        self._db.table(table_name).remove(doc_ids=[int(element_id)])
        return int(element_id)

    @staticmethod
    def create_query_condition(**filters):
        """:return: tinydb.queries.QueryInstance (default: noop)"""
        condition = Query().noop()
        if not filters:
            return condition

        entry = Query()
        for field, pattern in filters.items():
            if pattern is None and field in ["category", "end"]:
                # The 'category' and 'end' fields are of type string or None. The
                # condition is constructed depending on the filter pattern
                new_condition = entry[field] == None  # noqa
            elif field == "value":
                new_condition = entry[field] == float(pattern)
            else:
                new_condition = entry[field].search(pattern.lower())

            condition &= new_condition

        return condition

    def close(self):
        """Close the TinyDB database."""
        self._db.close()


class TinyDbPocket(Pocket):
    def __init__(self, name=None, data_dir=None, **kwargs):
        """Create a pocket with a TinyDB database backend, identified by 'name'.
        If 'data_dir' is given, the database storage type is JSON (the storage
        filepath is derived from the Pocket's name). Otherwise the data is
        stored in memory.
        Keyword args are passed to the TinyDB constructor. See the respective
        docs for detailed information.
        """

        # evaluate args/kwargs for TinyDB constructor. This overwrites the
        # 'storage' kwarg if explicitly passed
        if data_dir is None:
            args = []
            kwargs["storage"] = storages.MemoryStorage
        else:
            args = [os.path.join(data_dir, f"{name}.json")]
            kwargs["storage"] = storages.JSONStorage

        db_interface = TinyDbInterface(*args, **kwargs)
        super().__init__(db_interface, name=name)


TinyDB.default_table_name = DEFAULT_TABLE
