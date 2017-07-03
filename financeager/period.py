#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
from collections import defaultdict, Counter
from dateutil import rrule
from datetime import datetime as dt

from tinydb import TinyDB, Query, JSONStorage
from tinydb.database import Element
from tinydb.queries import QueryImpl

from .config import CONFIG_DIR, CONFIG
from .entries import CategoryEntry


# TODO temporary set to have module independent of items
DATE_FORMAT = CONFIG["DATABASE"]["date_format"]


class Period(object):

    DEFAULT_NAME = dt.today().year

    def __init__(self, name=None):
        self._name = "{}".format(Period.DEFAULT_NAME if name is None else name)

    @property
    def name(self):
        return self._name


class PeriodException(Exception):
    pass


class TinyDbPeriod(TinyDB, Period):

    def __init__(self, name=None, *args, **kwargs):
        """
        Create a period with a TinyDB database backend, identified by ``name``.
        The filepath arg for tinydb.JSONStorage is derived from the name.
        Keyword args are passed to the TinyDB constructor (f.i. storage type).
        """

        self._name = "{}".format(Period.DEFAULT_NAME if name is None else name)
        if kwargs.get("storage", JSONStorage) == JSONStorage:
            args = list(args) + [os.path.join(CONFIG_DIR, "{}.json".format(self._name))]
        super(TinyDbPeriod, self).__init__(*args, **kwargs)
        self._create_category_cache()

    def _create_category_cache(self):
        """The category cache assigns a counter for each element name in the
        database (excluding repetitive elements), keeping track of the
        categories the element was labeled with. This allows deriving the
        category of an element if not explicitly given."""
        self._category_cache = defaultdict(Counter)
        for element in self.all():
            self._category_cache[element["name"]].update([element["category"]])

    def add_entry(self, **kwargs):
        """
        Add an entry (standard or recurrent) to the database.
        Using the kwargs name, value[, category, date] inserts a unique entry
        in the standard table. Using the kwargs name, value, repetitive[, category]
        inserts a template entry in the repetitive table.

        Two kwargs are mandatory:
            :param name: entry name
            :type name: str
            :param value: entry value
            :type value: float, int or str

        The following kwarg is optional:
            :param category: entry category. If not specified, the program
                attempts to derive it from previous, eponymous entries. If this
                fails, ``CategoryEntry.DEFAULT_NAME`` is assigned
            :type category: str

        The following kwarg is optional for standard entries:
            :param date: entry date. If not specified, the current date is assigned
            :type date: str of ``DATE_FORMAT``

        The following kwarg is mandatory for recurrent entries:
            :param repetitive: frequency ('yearly', 'half-yearly', 'quarterly',
                'monthly', 'weekly' or 'daily'), start date (optional, defaults to
                current date) and end date (optional, defaults to last day of
                the period's year)
            :type repetitive: list[str]

        :return: TinyDB ID of new entry (int)
        """

        value = float(kwargs["value"])
        name = kwargs["name"].lower()
        date = kwargs.get("date")
        if date is None:
            # FIXME this will assign the current date to ANY period
            date = dt.today().strftime(DATE_FORMAT)
        category = kwargs.get("category")

        if category is None:
            if len(self._category_cache[name]) == 1:
                category = self._category_cache[name].most_common(1)[0][0]
            else:
                # assign default name (must be str), s.t. category field can be queried
                category = CategoryEntry.DEFAULT_NAME
        else:
            category = category.lower()

        self._category_cache[name].update([category])

        repetitive_args = kwargs.get("repetitive", False)
        if repetitive_args:
            frequency = repetitive_args[0].lower()
            start = dt.today().strftime(DATE_FORMAT)
            if len(repetitive_args) > 1:
                start = repetitive_args[1]
            end = None
            if len(repetitive_args) > 2:
                end = repetitive_args[2]
            element_id = self.table("repetitive").insert(
                    dict(
                        name=name, value=value, category=category,
                        frequency=frequency, start=start, end=end
                        ))
        else:
            element_id = self.insert(
                    dict(
                        name=name, value=value, date=date, category=category))
        return element_id

    def get_entry(self, eid=None, table_name=TinyDB.DEFAULT_TABLE):
        """
        Get entry specified by ``eid`` in the table ``table_name``.

        :type eid: int or str

        :raise: PeriodException if eid missing or element not found
        :return: found element (tinydb.Element)
        """

        if eid is None:
            raise PeriodException("No element ID specified.")

        element = self.table(table_name).get(eid=int(eid))
        if element is None:
            raise PeriodException("Element not found.")

        return element

    def _search_all_tables(self, query_impl=None, create_recurrent_elements=True):
        """
        Search both the standard table and the repetitive table for elements
        that satisfy the given condition.

        :param query_impl: condition for the search. If none (default), all elements are returned.
        :type query_impl: tinydb.queries.QueryImpl

        :param create_recurrent_elements: 'Expand' elements of the 'repetitive'
            table prior to search (used when printing) or not (used when deleting).
        :type create_recurrent_elements: bool

        :return: list[tinydb.Element]
        """

        elements = []
        if query_impl is None:
            elements.extend(self.all())
        else:
            elements.extend(self.search(query_impl))

        if create_recurrent_elements:
            for element in self.table("repetitive").all():
                for e in self._create_repetitive_elements(element):
                    if query_impl is None:
                        elements.append(e)
                    else:
                        if query_impl(e):
                            elements.append(e)
        else:
            if query_impl is None:
                elements.extend(self.table("repetitive").all())
            else:
                elements.extend(self.table("repetitive").search(query_impl))

        return elements

    def _create_repetitive_elements(self, element):
        name = element["name"]
        value = element["value"]
        category = element.get("category")
        frequency = element["frequency"].upper()
        start = element["start"]
        end = element.get("end")

        if end is None:
            end = dt.now()
            last_second = dt(int(self._name), 12, 31, 23, 59, 59)
            if end > last_second:
                end = last_second
        else:
            end = dt.strptime(end, DATE_FORMAT)

        rrule_kwargs = dict(
                dtstart=dt.strptime(start, DATE_FORMAT), until=end
                )
        interval = 1
        if frequency == "BIMONTHLY":
            frequency = "MONTHLY"
            interval = 2
        elif frequency == "QUARTER-YEARLY":
            frequency = "MONTHLY"
            interval = 3
        elif frequency == "HALF-YEARLY":
            frequency = "MONTHLY"
            interval = 6

        rrule_kwargs["interval"] = interval
        rule = rrule.rrule(getattr(rrule, frequency), **rrule_kwargs)

        for date in rule:
            element_name = name
            if frequency == "MONTHLY":
                element_name = "{} {}".format(name, date.strftime("%B").lower())
            yield Element(dict(
                name=element_name, value=value, category=category,
                date=date.strftime(DATE_FORMAT)
                ))

    def find_entry(self, create_recurrent_elements=True, **query_kwargs):
        condition = self._create_query_condition(**query_kwargs)
        return self._search_all_tables(condition,
                create_recurrent_elements=create_recurrent_elements)

    def remove_entry(self, **kwargs):
        """
        Remove an entry from the Period database.

        This can be achieved in two ways by providing suitable kwargs:
        a)
            :param eid: ID of the element to be deleted.
            :type eid: int or str
            :param table_name: name of the table that contains the element.
                Default: TinyDbPeriod.DEFAULT_TABLE
            :type table_name: str
        b)
            :param name: name of the element to be deleted
            :param date: date of the element to be deleted (optional)
            :param category: category of the element to be deleted (optional)
            A query is constructed from the given kwargs and used to search the
            entire database. If multiple entries match the query, nothing is
            removed.

        :raise: PeriodException if element/ID not found or ambiguous query.
        :return: element ID if removal was successful
        """

        entry_id = kwargs.get("eid")
        if entry_id is not None:
            entry_id = int(entry_id)
            table_name = kwargs.get("table_name", TinyDB.DEFAULT_TABLE)

            # might raise PeriodException if ID not existing
            entry = self.get_entry(eid=entry_id, table_name=table_name)

            self.table(table_name).remove(eids=[entry.eid])
            self._category_cache[entry["name"]][entry["category"]] -= 1
            return entry.eid

        entries = self.find_entry(create_recurrent_elements=False, **kwargs)
        if entries:
            if len(entries) > 1:
                raise PeriodException("Ambiguous query. Nothing is removed.")

            entry = entries[0]
            self._category_cache[entry["name"]][entry["category"]] -= 1

            entry_id = entry.eid

            if entry.get("frequency", False):
                self.table("repetitive").remove(eids=[entry_id])
            else:
                self.remove(eids=[entry_id])

            return entry_id

        raise PeriodException("No entry matching the query.")

    def _create_query_condition(self, name=None, value=None, category=None, date=None):
        condition = None
        entry = Query()

        for item_name in ["name", "value", "category", "date"]:
            item = locals()[item_name]
            if item is None:
                continue

            if isinstance(item, str):
                item = item.lower()

            #TODO use tinydb.Query.search
            new_condition = (entry[item_name].matches(".*{}.*".format(item)))
            if condition is None:
                condition = new_condition
            else:
                condition &= new_condition

        return condition

    def print_entries(self, **query_kwargs):
        condition = self._create_query_condition(**query_kwargs)
        return {"elements": self._search_all_tables(condition)}


TinyDB.DEFAULT_TABLE = "standard"
