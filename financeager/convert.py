"""Conversion of 'period' into 'pocket' database format."""
import glob
import os.path

from tinydb import database

import financeager

from . import exceptions, pocket


def main(*, sinks, period_filepaths=None):
    """Validate given period filepaths and run conversion. If no filepaths
    given, use all JSON files in `financeager.DATA_DIR`.
    Return True on success, otherwise False.
    """
    if period_filepaths is None:
        period_filepaths = sorted(
            glob.glob(os.path.join(financeager.DATA_DIR, "*.json"))
        )
    else:
        non_existing_filepaths = [f for f in period_filepaths if not os.path.exists(f)]
        if non_existing_filepaths:
            sinks.error(
                exceptions.ConversionError(
                    "One or more non-existing filepaths:\n{}".format(
                        "\n".join(non_existing_filepaths)
                    )
                )
            )
            return False

    period_filepaths = [
        f
        for f in period_filepaths
        if not f.endswith(f"{financeager.DEFAULT_POCKET_NAME}.json")
    ]

    invalid_filepaths = []
    for filepath in period_filepaths:
        try:
            _extract_year_from_filepath(filepath)
        except ValueError:
            invalid_filepaths.append(filepath)
    if invalid_filepaths:
        sinks.error(
            exceptions.ConversionError(
                "One or more invalid filepaths:\n{}".format(
                    "\n".join(invalid_filepaths)
                )
            )
        )
        return False

    sinks.info(f"Converting {len(period_filepaths)} period(s)...")
    run(period_filepaths)
    return True


def run(period_filepaths):
    """Read in period databases at given filepaths and create a single main
    Pocket from their contents. Date-related fields are updated with the
    according year.
    It has to be guaranteed that the period filepaths exist.
    """
    main_pocket = pocket.TinyDbPocket(data_dir=financeager.DATA_DIR)

    for filepath in period_filepaths:
        year = _extract_year_from_filepath(filepath)

        with database.TinyDB(filepath) as db:
            table_name = financeager.DEFAULT_TABLE
            documents = db.table(table_name).all()
            for doc in documents:
                doc["date"] = f"{year}-{doc['date']}"
            main_pocket._db.table(table_name).insert_multiple(documents)

            table_name = financeager.RECURRENT_TABLE
            documents = db.table(table_name).all()
            for doc in documents:
                doc["start"] = f"{year}-{doc['start']}"
                doc["end"] = f"{year}-{doc['end']}"
            main_pocket._db.table(table_name).insert_multiple(documents)

    main_pocket.close()


def _extract_year_from_filepath(filepath):
    return int(os.path.splitext(os.path.basename(filepath))[0])
