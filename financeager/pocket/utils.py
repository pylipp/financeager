"""Utility classes for abstracting database operations."""

from abc import ABC, abstractmethod
from typing import Any, Iterable


class DatabaseInterface(ABC):
    """Abstract base class for database client implementations."""

    @abstractmethod
    def retrieve(self, table_name, condition=None) -> Iterable[dict]:
        """Retrieve rows from a table.

        :param table_name: name of the table to query
        :param condition: optional condition to filter rows
        :return: list of dicts
        """

    @abstractmethod
    def retrieve_by_id(self, table_name, element_id) -> dict[bytes, Any] | None:
        """Retrieve a single row by its ID.

        :param table_name: name of the table to query
        :param element_id: ID of the element to retrieve
        :return: dict or None if ID does not exist
        """

    @abstractmethod
    def create(self, table_name, data) -> int:
        """Create a new row in a table.

        :param table_name: name of the table
        :param data: dict of data to insert
        :return: ID of the created element
        """

    @abstractmethod
    def update_by_id(self, table_name, element_id, data) -> int:
        """Update a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to update
        :param data: dict of data to update
        :return: ID of the updated element
        """

    @abstractmethod
    def delete_by_id(self, table_name, element_id) -> int:
        """Delete a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to delete
        :return: ID of the deleted element
        """

    @staticmethod
    @abstractmethod
    def create_query_condition(**filters) -> Any:
        """Construct query condition according to given filters. A filter is
        given by a key-value pair. The key indicates the field, the value the
        pattern to filter for. Valid keys are 'name', 'date', 'value' and/or
        'category'. Patterns must be of type string, or None (only for the fields
        'category' and 'end'); indicates filtering for all entries of the default
        category, and recurrent entries with indefinite end, resp.).
        Return a condition object that is comprehended by the database interface (i.e.
        DatabaseInterface.retrieve).
        """

    @abstractmethod
    def close(self) -> None:
        """Close underlying database."""
