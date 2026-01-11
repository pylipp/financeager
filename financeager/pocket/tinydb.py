import os.path
from collections import defaultdict

from tinydb import Query, TinyDB, storages

from .. import DEFAULT_TABLE, RECURRENT_TABLE
from .base import Pocket
from .utils import DatabaseClient


class TinyDbClient(DatabaseClient):
    """Database client implementation using TinyDB."""

    def __init__(self, *args, **kwargs):
        """Initialize TinyDB instance.

        :param args: positional arguments for TinyDB constructor
        :param kwargs: keyword arguments for TinyDB constructor
        """
        self._db = TinyDB(*args, **kwargs)

    def retrieve(self, table_name, condition=None):
        if condition is None:
            return self._db.table(table_name).all()
        return self._db.table(table_name).search(condition)

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
        """Construct query condition according to given filters. A filter is
        given by a key-value pair. The key indicates the field, the value the
        pattern to filter for. Valid keys are 'name', 'date', 'value' and/or
        'category'. Patterns must be of type string, or None (only for the fields
        'category' and 'end'); indicates filtering for all entries of the default
        category, and recurrent entries with indefinite end, resp.).
        :return: tinydb.queries.QueryInstance (default: noop)
        """
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

        db_client = TinyDbClient(*args, **kwargs)
        super().__init__(db_client, name=name)

    def _search_all_tables(self, condition):
        """Search both the standard table and the recurrent table for elements
        that satisfy the given condition.

        The entries' `doc_id` attribute is used as key in the returned subdicts
        because it is lost in the client-server communication protocol (on
        `financeager print`, the server calls Pocket.get_entries, yet the
        JSON response returned drops the Document.doc_id attribute s.t. it's not
        available when calling prettify on the client side).

        :param condition: condition for the search
        :type condition: tinydb.queries.QueryInstance

        :return: dict
        """

        elements = {DEFAULT_TABLE: {}, RECURRENT_TABLE: defaultdict(list)}

        for element in self.db_client.retrieve(DEFAULT_TABLE, condition):
            elements[DEFAULT_TABLE][element.doc_id] = dict(element)

        # all recurrent elements are generated, and the ones matching the
        # condition are appended to a list that is stored under their generating
        # element's doc_id in the 'recurrent' subdictionary
        for element in self.db_client.retrieve(RECURRENT_TABLE):
            for e in self._create_recurrent_elements(element):
                if condition(e):
                    elements[RECURRENT_TABLE][element.doc_id].append(e)

        return elements

    def get_entries(self, filters=None, recurrent_only=False):
        """Get entries using TinyDB backend.

        Constructs a condition from the given filters and uses it to query all tables.

        :return: dict{
                    DEFAULT_TABLE:  dict{ int: tinydb.Document },
                    RECURRENT_TABLE: dict{ int: list[tinydb.Document] }
                    } or
                 list[tinydb.Document]
        """
        filters = filters or {}
        condition = TinyDbClient.create_query_condition(**filters)

        if recurrent_only:
            # Flatten tinydb Document into dict
            return [
                {**e, **{"eid": e.doc_id}}
                for e in self.db_client.retrieve(RECURRENT_TABLE, condition)
            ]

        return self._search_all_tables(condition)

    def close(self):
        """Close TinyDB database."""
        self.db_client.close()


TinyDB.default_table_name = DEFAULT_TABLE
