"""Migration utilities for converting TinyDB pockets to SQLite pockets."""

import json
import os.path

from tinydb import TinyDB

from .. import DEFAULT_TABLE, RECURRENT_TABLE, init_logger
from .sqlite import SqlitePocket

logger = init_logger(__name__)


def migrate_pocket(pocket_name, data_dir):
    """Migrate a TinyDB pocket to SQLite format.

    :param pocket_name: name of the pocket to migrate (without extension)
    :param data_dir: directory containing the pocket files
    :return: dict with migration statistics
    :raises: FileNotFoundError if TinyDB file doesn't exist
    :raises: json.JSONDecodeError if TinyDB file contains invalid JSON
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
        raise json.JSONDecodeError(
            f"Invalid JSON in {tinydb_path}: {e.msg}", e.doc, e.pos
        )

    # Load TinyDB
    tinydb = TinyDB(tinydb_path)

    # Open SqlitePocket
    sqlite_pocket = SqlitePocket(name=pocket_name, data_dir=data_dir)

    # Migrate standard table
    standard_entries = tinydb.table(DEFAULT_TABLE).all()
    standard_count = 0
    for entry in standard_entries:
        doc_id = entry.doc_id
        entry_data = dict(entry)
        # Insert with specific eid
        query = (
            f"INSERT INTO {DEFAULT_TABLE} "
            "(eid, name, date, category, value) VALUES (?, ?, ?, ?, ?)"
        )
        sqlite_pocket.db_interface._conn.execute(
            query,
            (
                doc_id,
                entry_data["name"],
                entry_data["date"],
                entry_data.get("category"),
                entry_data["value"],
            ),
        )
        standard_count += 1

    # Migrate recurrent table
    recurrent_entries = tinydb.table(RECURRENT_TABLE).all()
    recurrent_count = 0
    for entry in recurrent_entries:
        doc_id = entry.doc_id
        entry_data = dict(entry)
        # Insert with specific eid
        query = (
            f"INSERT INTO {RECURRENT_TABLE} "
            "(eid, name, start, end, frequency, category, value) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        sqlite_pocket.db_interface._conn.execute(
            query,
            (
                doc_id,
                entry_data["name"],
                entry_data["start"],
                entry_data.get("end"),
                entry_data["frequency"],
                entry_data.get("category"),
                entry_data["value"],
            ),
        )
        recurrent_count += 1

    # Commit changes
    sqlite_pocket.db_interface._conn.commit()

    # Close databases
    tinydb.close()
    sqlite_pocket.close()

    total_count = standard_count + recurrent_count
    return {
        "pocket_name": pocket_name,
        "standard_count": standard_count,
        "recurrent_count": recurrent_count,
        "total_count": total_count,
    }
