"""Database utility classes for abstracting database operations."""

from abc import ABC, abstractmethod

from tinydb import Query, TinyDB


class DatabaseClient(ABC):
    """Abstract base class for database client implementations."""

    @abstractmethod
    def retrieve(self, table_name, condition=None):
        """Retrieve rows from a table.

        :param table_name: name of the table to query
        :param condition: optional condition to filter rows
        :return: list of dicts
        """

    @abstractmethod
    def retrieve_by_id(self, table_name, element_id):
        """Retrieve a single row by its ID.

        :param table_name: name of the table to query
        :param element_id: ID of the element to retrieve
        :return: dict or None if ID does not exist
        """

    @abstractmethod
    def create(self, table_name, data):
        """Create a new row in a table.

        :param table_name: name of the table
        :param data: dict of data to insert
        :return: ID of the created element
        """

    @abstractmethod
    def update_by_id(self, table_name, element_id, data):
        """Update a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to update
        :param data: dict of data to update
        :return: ID of the updated element
        """

    @abstractmethod
    def delete_by_id(self, table_name, element_id):
        """Delete a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to delete
        :return: ID of the deleted element
        """


class TinyDbClient(DatabaseClient):
    """Database client implementation using TinyDB."""

    def __init__(self, *args, **kwargs):
        """Initialize TinyDB instance.

        :param args: positional arguments for TinyDB constructor
        :param kwargs: keyword arguments for TinyDB constructor
        """
        self._db = TinyDB(*args, **kwargs)

    def retrieve(self, table_name, condition=None):
        """Retrieve rows from a table.

        :param table_name: name of the table to query
        :param condition: optional TinyDB query condition
        :return: list of dicts (TinyDB Documents)
        """
        if condition is None:
            return self._db.table(table_name).all()
        return self._db.table(table_name).search(condition)

    def retrieve_by_id(self, table_name, element_id):
        """Retrieve a single row by its ID.

        :param table_name: name of the table to query
        :param element_id: ID of the element to retrieve
        :return: dict (TinyDB Document) or None if ID does not exist
        """
        return self._db.table(table_name).get(doc_id=int(element_id))

    def create(self, table_name, data):
        """Create a new row in a table.

        :param table_name: name of the table
        :param data: dict of data to insert
        :return: ID of the created element
        """
        return self._db.table(table_name).insert(data)

    def update_by_id(self, table_name, element_id, data):
        """Update a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to update
        :param data: dict of data to update
        :return: ID of the updated element
        """
        return self._db.table(table_name).update(data, doc_ids=[int(element_id)])[0]

    def delete_by_id(self, table_name, element_id):
        """Delete a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to delete
        :return: ID of the deleted element
        """
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
