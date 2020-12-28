"""Conversion of 'period' into 'pocket' database format."""
from tinydb import database

import financeager

from . import pocket


def run(period_filepaths):
    """Read in period databases at given filepaths and create a single 'main'
    Pocket from their contents.
    It has to be guaranteed that the period filepaths exist.
    """
    main_pocket = pocket.TinyDbPocket(
        data_dir=financeager.DATA_DIR, name="main")

    for filepath in period_filepaths:
        with database.TinyDB(filepath) as db:
            for table_name in db.tables():
                main_pocket._db.table(table_name).insert_multiple(
                    db.table(table_name).all())

    main_pocket.close()
