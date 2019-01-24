#!/usr/bin/env python
"""Script to parse monthly CSV bank statement for relevant entries to add to the
financeager database."""

import os
import sys
from datetime import datetime as dt
import csv

from financeager.cli import run
from financeager import PERIOD_DATE_FORMAT

script_dir = os.path.dirname(os.path.abspath(__file__))
data_file = sys.argv[1]
if not os.path.isabs(data_file):
    filepath = os.path.join(script_dir, data_file)
else:
    filepath = os.path.expanduser(data_file)


class SemicolonDialect(csv.excel):
    delimiter = ';'


f = open(filepath, encoding="windows-1252")
data = csv.DictReader(f, dialect=SemicolonDialect)

# all supermarket shopping shall go to the database
trigger_words = [
    "lidl", "rewe", "aldi", "dm fil", "denns", "kaufland", "tengelmann",
    "edeka", "denn.s", "alnatura", "bioladen"
]

# when adding an unknown entry, you might want to specify the corresponding
# category if you don't want the default category to be assigned
categories = {}

entries_rest = []

for row in data:
    try:
        name = row["Beguenstigter/Zahlungspflichtiger"]
        name = name.lower()
    except AttributeError:
        # last row (Abschluss/Entgeltabrechnung) contains no data
        continue

    value = row["Betrag"].replace(",", ".")
    date = dt.strptime(row["Buchungstag"], "%d.%m.%y")
    month_day = date.strftime(PERIOD_DATE_FORMAT)

    for word in trigger_words:
        if word in name:
            print("{} {}: {}".format(month_day, word, value))
            run(command="add",
                name=word,
                value=value,
                date=month_day,
                period=date.year,
                category=categories.get(word, "groceries"))
            break
    else:
        entries_rest.append((month_day, name, value))

f.close()

# show anything that was not added
if entries_rest:
    print(80 * "=")

for entry in entries_rest:
    print("{} {}: {}".format(*entry))
