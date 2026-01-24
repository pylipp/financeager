"""Migration utilities for converting TinyDB pockets to SQLite pockets."""

import json
import os.path

from tinydb import TinyDB

from .. import DEFAULT_TABLE, RECURRENT_TABLE
from .sqlite import SqlitePocket


def migrate_pocket(pocket_name, data_dir):
    """Migrate a TinyDB pocket to SQLite format.

    :param pocket_name: name of the pocket to migrate (without extension)
    :param data_dir: directory containing the pocket files
    :return: dict with migration statistics
    :raises: FileNotFoundError if TinyDB file doesn't exist
    :raises: ValueError if TinyDB file contains invalid JSON
    :raises: Exception for other errors during migration
    """
    # Validate that TinyDB file exists
    tinydb_path = os.path.join(data_dir, f"{pocket_name}.json")
    if not os.path.exists(tinydb_path):
        raise FileNotFoundError(f"TinyDB file not found: {tinydb_path}")

    # Validate JSON before attempting to open with TinyDB
    try:
        with open(tinydb_path, "r") as f:
            content = f.read()
            # Handle empty file case (valid for TinyDB)
            if content.strip():
                json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {tinydb_path}: {e.msg}")

    # Load TinyDB
    tinydb = TinyDB(tinydb_path)

    # Check if SQLite file already exists
    sqlite_path = os.path.join(data_dir, f"{pocket_name}.sqlite")
    if os.path.exists(sqlite_path):
        tinydb.close()
        raise FileExistsError(
            f"SQLite file already exists: {sqlite_path}. "
            "Please remove or rename it before migrating."
        )

    # Open SqlitePocket
    sqlite_pocket = SqlitePocket(name=pocket_name, data_dir=data_dir)

    # Get the database connection for direct migration
    # We need direct access to insert with specific eid values
    # Note: Table names (DEFAULT_TABLE, RECURRENT_TABLE) are validated
    # module constants, making f-string usage safe here
    conn = sqlite_pocket.db_interface._conn

    # Migrate standard table using bulk insert
    standard_entries = tinydb.table(DEFAULT_TABLE).all()
    if standard_entries:
        standard_data = [
            (
                entry.doc_id,
                entry["name"],
                entry["date"],
                entry.get("category"),
                entry["value"],
            )
            for entry in standard_entries
        ]
        conn.executemany(
            f"INSERT INTO {DEFAULT_TABLE} "
            "(eid, name, date, category, value) VALUES (?, ?, ?, ?, ?)",
            standard_data,
        )
    standard_count = len(standard_entries)

    # Migrate recurrent table using bulk insert
    recurrent_entries = tinydb.table(RECURRENT_TABLE).all()
    if recurrent_entries:
        recurrent_data = [
            (
                entry.doc_id,
                entry["name"],
                entry["start"],
                entry.get("end"),
                entry["frequency"],
                entry.get("category"),
                entry["value"],
            )
            for entry in recurrent_entries
        ]
        conn.executemany(
            f"INSERT INTO {RECURRENT_TABLE} "
            "(eid, name, start, end, frequency, category, value) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            recurrent_data,
        )
    recurrent_count = len(recurrent_entries)

    # Commit changes
    conn.commit()

    # Close databases
    tinydb.close()
    sqlite_pocket.close()

    return {
        "pocket_name": pocket_name,
        "standard_count": standard_count,
        "recurrent_count": recurrent_count,
        "total_count": standard_count + recurrent_count,
    }
