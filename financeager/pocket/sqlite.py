import os.path
import re
import sqlite3

from .. import DEFAULT_TABLE
from .base import Pocket
from .utils import DatabaseInterface


class SqliteInterface(DatabaseInterface):
    """Database interface implementation using SQLite."""

    def __init__(self, *args, **kwargs):
        """Initialize SQLite database connection.

        :param args: positional arguments for sqlite3.connect
        :param kwargs: keyword arguments for sqlite3.connect
        """
        self._conn = sqlite3.connect(*args, **kwargs)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create tables if they don't exist."""
        cursor = self._conn.cursor()
        
        # Create standard table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS standard (
                eid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                value REAL NOT NULL
            )
        """)
        
        # Create recurrent table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurrent (
                eid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT,
                frequency TEXT NOT NULL,
                category TEXT,
                value REAL NOT NULL
            )
        """)
        
        self._conn.commit()

    def retrieve(self, table_name, condition=None):
        """Retrieve rows from a table.

        :param table_name: name of the table to query
        :param condition: optional condition function to filter rows
        :return: list of dicts
        """
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Convert rows to dicts
        elements = []
        for row in rows:
            element = dict(row)
            elements.append(element)
        
        # Apply condition filter if provided
        if condition is not None:
            elements = [e for e in elements if condition(e)]
        
        return elements

    def retrieve_by_id(self, table_name, element_id):
        """Retrieve a single row by its ID.

        :param table_name: name of the table to query
        :param element_id: ID of the element to retrieve
        :return: dict or None if ID does not exist
        """
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE eid = ?", (element_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        # Convert to dict and exclude eid field to match TinyDB behavior
        result = dict(row)
        result.pop('eid', None)
        return result

    def create(self, table_name, data):
        """Create a new row in a table.

        :param table_name: name of the table
        :param data: dict of data to insert
        :return: ID of the created element
        """
        cursor = self._conn.cursor()
        
        # Build INSERT statement
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())
        
        cursor.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
            values
        )
        self._conn.commit()
        
        return cursor.lastrowid

    def update_by_id(self, table_name, element_id, data):
        """Update a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to update
        :param data: dict of data to update
        :return: ID of the updated element
        """
        cursor = self._conn.cursor()
        
        # Build UPDATE statement
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + (element_id,)
        
        cursor.execute(
            f"UPDATE {table_name} SET {set_clause} WHERE eid = ?",
            values
        )
        self._conn.commit()
        
        return element_id

    def delete_by_id(self, table_name, element_id):
        """Delete a row by its ID.

        :param table_name: name of the table
        :param element_id: ID of the element to delete
        :return: ID of the deleted element
        """
        cursor = self._conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE eid = ?", (element_id,))
        self._conn.commit()
        
        return element_id

    @staticmethod
    def create_query_condition(**filters):
        """Construct query condition function according to given filters.
        
        :return: function that takes a row dict and returns bool
        """
        if not filters:
            return lambda row: True
        
        def condition(row):
            for field, pattern in filters.items():
                if pattern is None and field in ["category", "end"]:
                    # Filter for None values
                    if row.get(field) is not None:
                        return False
                elif field == "value":
                    # Exact match for value
                    if row.get(field) != float(pattern):
                        return False
                else:
                    # Pattern matching for string fields
                    value = row.get(field)
                    if value is None:
                        return False
                    if pattern.lower() not in str(value).lower():
                        return False
            return True
        
        return condition

    def close(self):
        """Close the SQLite database connection."""
        self._conn.close()


class SqlitePocket(Pocket):
    def __init__(self, name=None, data_dir=None, **kwargs):
        """Create a pocket with an SQLite database backend, identified by 'name'.
        
        If 'data_dir' is given, the database is stored in a file with the
        .sqlite extension. Otherwise the data is stored in memory.
        
        Keyword args are passed to the sqlite3.connect constructor. See the
        respective docs for detailed information.
        """
        # Determine database path
        if data_dir is None:
            # In-memory database
            db_path = ":memory:"
        else:
            # File-based database
            db_path = os.path.join(data_dir, f"{name}.sqlite")
        
        db_interface = SqliteInterface(db_path, **kwargs)
        super().__init__(db_interface, name=name)
