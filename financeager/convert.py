"""Conversion of 'period' into 'pocket' database format."""
import os.path

from tinydb import database

import financeager

from . import pocket


def run(period_filepaths):
    """Read in period databases at given filepaths and create a single 'main'
    Pocket from their contents. Date-related fields are updated with the
    according year.
    It has to be guaranteed that the period filepaths exist.
    """
    main_pocket = pocket.TinyDbPocket(
        data_dir=financeager.DATA_DIR, name="main")

    for filepath in period_filepaths:
        year = int(os.path.splitext(os.path.basename(filepath))[0])

        with database.TinyDB(filepath) as db:
            table_name = financeager.DEFAULT_TABLE
            documents = db.table(table_name).all()
            for doc in documents:
                doc["date"] = "{}-{}".format(year, doc["date"])
            main_pocket._db.table(table_name).insert_multiple(documents)

            table_name = "recurrent"
            documents = db.table(table_name).all()
            for doc in documents:
                doc["start"] = "{}-{}".format(year, doc["start"])
                doc["end"] = "{}-{}".format(year, doc["end"])
            main_pocket._db.table(table_name).insert_multiple(documents)

    main_pocket.close()
