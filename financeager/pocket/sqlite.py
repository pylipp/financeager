import os.path
import sqlite3

from .base import Pocket
from .utils import DatabaseInterface


class SqliteInterface(DatabaseInterface):
    """Database interface implementation using SQLite."""

    # Valid table names for security
    _VALID_TABLES = {"standard", "recurrent"}
    # Valid column names for each table
    _VALID_COLUMNS = {
        "standard": {"name", "date", "category", "value"},
        "recurrent": {"name", "start", "end", "frequency", "category", "value"},
    }

    def __init__(self, *args, **kwargs):
        """Initialize SQLite database connection.

        :param args: positional arguments for sqlite3.connect
        :param kwargs: keyword arguments for sqlite3.connect
        """
        self._conn = sqlite3.connect(*args, **kwargs)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _validate_table_name(self, table_name):
        """Validate table name to prevent SQL injection.

        :param table_name: name of the table
        :raise ValueError: if table name is invalid
        """
        if table_name not in self._VALID_TABLES:
            raise ValueError(f"Invalid table name: {table_name}")

    def _validate_columns(self, table_name, columns):
        """Validate column names to prevent SQL injection.

        :param table_name: name of the table
        :param columns: iterable of column names
        :raise ValueError: if any column name is invalid
        """
        valid_columns = self._VALID_COLUMNS.get(table_name, set())
        for col in columns:
            if col not in valid_columns:
                raise ValueError(f"Invalid column name for {table_name}: {col}")

    def _create_tables(self):
        """Create tables if they don't exist."""
        cursor = self._conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS standard (
                eid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT,
                value REAL NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recurrent (
                eid INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT,
                frequency TEXT NOT NULL,
                category TEXT,
                value REAL NOT NULL
            )
        """
        )

        self._conn.commit()

    def retrieve(self, table_name, condition=None):
        self._validate_table_name(table_name)
        cursor = self._conn.cursor()

        # Optimize simple conditions by pushing them into SQL when possible.
        # For complex conditions (e.g., callables), fall back to Python filtering.
        if condition is None:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            elements = []
            for row in rows:
                elements.append(dict(row))
            return elements

        # Fast path: condition given as a dict of {column: value} for equality checks.
        if isinstance(condition, dict) and condition:
            self._validate_columns(table_name, condition.keys())
            where_clauses = []
            params = []
            for col, val in condition.items():
                where_clauses.append(f"{col} = ?")
                params.append(val)
            where_sql = " AND ".join(where_clauses)
            query = f"SELECT * FROM {table_name} WHERE {where_sql}"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            elements = []
            for row in rows:
                elements.append(dict(row))
            return elements

        # Fallback: retrieve all rows and filter in Python using the provided condition.
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        elements = []
        for row in rows:
            elements.append(dict(row))

        elements = [e for e in elements if condition(e)]
        return elements

    def retrieve_by_id(self, table_name, element_id):
        self._validate_table_name(table_name)
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE eid = ?", (element_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        # Convert to dict and exclude eid field to match TinyDB behavior
        result = dict(row)
        result.pop("eid", None)
        return result

    def create(self, table_name, data):
        self._validate_table_name(table_name)
        self._validate_columns(table_name, data.keys())
        cursor = self._conn.cursor()

        # Build INSERT statement
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())

        cursor.execute(
            f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values
        )
        self._conn.commit()

        return cursor.lastrowid

    def update_by_id(self, table_name, element_id, data):
        self._validate_table_name(table_name)

        # Handle empty data dictionary (all None values filtered out)
        if not data:
            return element_id

        self._validate_columns(table_name, data.keys())
        cursor = self._conn.cursor()

        # Build UPDATE statement
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = tuple(data.values()) + (element_id,)

        cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE eid = ?", values)
        self._conn.commit()

        return element_id

    def delete_by_id(self, table_name, element_id):
        self._validate_table_name(table_name)
        cursor = self._conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE eid = ?", (element_id,))
        self._conn.commit()

        return element_id

    @staticmethod
    def create_query_condition(**filters):
        """:return: function that takes a row dict and returns bool"""
        if not filters:
            return lambda _: True

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
        if data_dir is None:
            db_path = ":memory:"
        else:
            db_path = os.path.join(data_dir, f"{name}.sqlite")

        db_interface = SqliteInterface(db_path, **kwargs)
        super().__init__(db_interface, name=name)
