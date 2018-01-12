"""Defines Period database object holding per-year financial data."""

from __future__ import unicode_literals

import os.path
from collections import defaultdict, Counter
from dateutil import rrule
from datetime import datetime as dt

from tinydb import TinyDB, Query, storages
from tinydb.database import Element
from schematics.models import Model as SchematicsModel
from schematics.types import StringType, FloatType, DateType
from schematics.exceptions import DataError, ValidationError

from . import PERIOD_DATE_FORMAT
from .entries import CategoryEntry


# format for ValidationModel.to_primitive() call
DateType.SERIALIZED_FORMAT = PERIOD_DATE_FORMAT


class BaseValidationModel(SchematicsModel):
    name = StringType(min_length=1, required=True)
    value = FloatType(required=True)
    category = StringType(min_length=1)


class StandardEntryValidationModel(BaseValidationModel):
    date = DateType(formats=("%Y-%m-%d", PERIOD_DATE_FORMAT))


class RecurrentEntryValidationModel(BaseValidationModel):
    frequency = StringType(choices=["yearly", "half-yearly", "quarter-yearly",
        "bimonthly", "monthly", "weekly", "daily"], required=True)
    start = DateType(formats=("%Y-%m-%d", PERIOD_DATE_FORMAT))
    end = DateType(formats=("%Y-%m-%d", PERIOD_DATE_FORMAT))


class Period(object):

    DEFAULT_YEAR = dt.today().year
    DEFAULT_NAME = str(DEFAULT_YEAR)

    def __init__(self, name=None):
        """Create Period object. Its name defaults to the current year if not
        specified.
        """
        self._name = "{}".format(name or Period.DEFAULT_NAME)

    @property
    def name(self):
        return self._name

    @property
    def year(self):
        """Return period year as integer."""
        return int(self._name)


class PeriodException(Exception):
    pass


class TinyDbPeriod(Period):

    DEFAULT_TABLE = "standard"

    def __init__(self, name=None, data_dir=None, **kwargs):
        """Create a period with a TinyDB database backend, identified by 'name'.
        If 'data_dir' is given, the database storage type is JSON (the storage
        filepath is derived from the Period's name). Otherwise the data is
        stored in memory.
        Keyword args are passed to the TinyDB constructor. See the respective
        docs for detailed information.
        """

        super().__init__(name=name)

        # evaluate args/kwargs for TinyDB constructor. This overwrites the
        # 'storage' kwarg if explicitly passed
        if data_dir is None:
            args = []
            kwargs["storage"] = storages.MemoryStorage
        else:
            args = [os.path.join(data_dir, "{}.json".format(self.name))]
            kwargs["storage"] = storages.JSONStorage

        self._db = TinyDB(*args, **kwargs)
        self._create_category_cache()

    def _create_category_cache(self):
        """The category cache assigns a counter for each element name in the
        database (excluding recurrent elements), keeping track of the
        categories the element was labeled with. This allows deriving the
        category of an element if not explicitly given."""
        self._category_cache = defaultdict(Counter)
        for element in self._db.all():
            self._category_cache[element["name"]].update([element["category"]])

    def _preprocess_entry(self, raw_data=None, table_name=None, partial=False):
        """Perform preprocessing steps (validation, conversion, substitution) of
        raw entry fields prior to adding it to the database.

        :param raw_data: dict containing raw entry fields
        :param table_name: name of the table that the entry is passed to
        :param partial: indicates whether preprocessing is performed before
            adding (False) or updating (True) the database

        :raise: PeriodException if validation failed or table name unknown
        """

        table_name = table_name or TinyDbPeriod.DEFAULT_TABLE
        if table_name not in ["recurrent", TinyDbPeriod.DEFAULT_TABLE]:
            raise PeriodException("Unknown table name: {}".format(table_name))

        self._remove_redundant_fields(table_name, raw_data)

        validated_fields = self._validate_entry(raw_data=raw_data,
                table_name=table_name, partial=partial)
        converted_fields = self._convert_fields(**validated_fields)

        if not partial:
            converted_fields = self._substitute_none_fields(
                    table_name=table_name, **converted_fields)

        return converted_fields

    @staticmethod
    def _remove_redundant_fields(table_name, raw_data):
        """The raw data (e.g. parsed from the command line) might contain fields
        that are not required by the given table type and hence, they crash the
        schematics validation ('Rogue field' error). This method removes
        redundant fields in `raw_data` in-place.
        """

        if table_name == "recurrent":
            redundant_fields = ["date"]
        else:
            redundant_fields = ["start", "end", "frequency"]

        for field in redundant_fields:
            raw_data.pop(field, None)

    @staticmethod
    def _validate_entry(raw_data, table_name, **model_kwargs):
        """Validate raw entry data acc. to ValidationModel.

        :return: primitive (type-correct) representation of fields
        :raise: PeriodException if validation failed
        """

        ValidationModel = RecurrentEntryValidationModel \
            if table_name == "recurrent" else StandardEntryValidationModel

        try:
            # pass the kwargs twice because schematics API is inconsistent...
            validation_model = ValidationModel(raw_data=raw_data,
                    **model_kwargs)
            validation_model.validate(**model_kwargs)
            return validation_model.to_primitive()
        except (DataError, ValidationError) as e:
            raise PeriodException("Invalid input data: {}".format(e.messages))

    @staticmethod
    def _convert_fields(**fields):
        """Convert string field values to lowercase for storage. Fields with
        value None are discarded.
        """

        converted_fields = {}

        for k, v in fields.items():
            if v is None:
                continue
            try:
                converted_fields[k] = v.lower()
            except AttributeError:
                converted_fields[k] = v

        return converted_fields

    def _substitute_none_fields(self, table_name, **fields):
        """Substitute optional fields by defaults."""

        substituted_fields = fields.copy()

        if table_name == "recurrent":
            if fields.get("start") is None:
                substituted_fields["start"] = dt.today().strftime(PERIOD_DATE_FORMAT)
            if fields.get("end") is None:
                substituted_fields["end"] = \
                    dt.today().replace(month=12, day=31).strftime(PERIOD_DATE_FORMAT)

        elif table_name == TinyDbPeriod.DEFAULT_TABLE:
            if fields.get("date") is None:
                substituted_fields["date"] = dt.today().strftime(PERIOD_DATE_FORMAT)

        if fields.get("category") is None:
            name = fields["name"]
            # TODO take most common, raise Exception if not clear.
            # return element info instead of ID
            if len(self._category_cache[name]) == 1:
                category = self._category_cache[name].most_common(1)[0][0]
            else:
                # assign default name (must be str), s.t. category field can be queried
                # TODO: reconsider this
                category = CategoryEntry.DEFAULT_NAME
            substituted_fields["category"] = category

        return substituted_fields

    def _update_category_cache(self, eid=None, table_name=None, removing=False,
            **fields):
        """Update the category cache when adding or updating an entry. The `eid`
        kwarg is used to distinguish the use cases.

        :param eid: element ID when updating
        :param table_name: table name when updating
        :param removing: indicate updating cache after removing an entry
        :param fields: preprossed entry fields to be inserted in the database

        :raise: PeriodException if element not found when updating
        """

        if eid is None:
            name = fields["name"]
            category = fields["category"]
            if removing:
                self._category_cache[name][category] -= 1
            else:
                self._category_cache[name].update([category])
        else:
            # raises a PeriodException if eid is not found
            old_entry = self.get_entry(eid=eid, table_name=table_name)
            old_name = old_entry["name"]
            old_category = old_entry["category"]

            # update category cache if one of name or category was changed
            if fields.get("name") is not None or \
                    fields.get("category") is not None:
                self._category_cache[old_name][old_category] -= 1
                self._category_cache[fields.get("name") or old_name][
                        fields.get("category") or old_category] += 1

    def add_entry(self, table_name=None, **kwargs):
        """
        Add an entry (standard or recurrent) to the database.
        If 'table_name' is not specified, the kwargs name, value[, category, date]
        are used to insert a unique entry in the standard table.
        With 'table_name' as 'recurrent', the kwargs name, value, frequency[, start,
        end, category] are used to insert a template entry in the recurrent table.

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
            :type date: str of ``PERIOD_DATE_FORMAT``

        The following kwarg is mandatory for recurrent entries:
            :param frequency: 'yearly', 'half-yearly', 'quarter-yearly',
                'bimonthly', 'monthly', 'weekly' or 'daily'

        The following kwargs are optional for recurrent entries:
            :param start: start date (defaults to current date)
            :param end: end date (defaults to last day of the period's year)

        :raise: PeriodException if validation failed or table name unknown
        :return: TinyDB ID of new entry (int)
        """

        table_name = table_name or TinyDbPeriod.DEFAULT_TABLE
        fields = self._preprocess_entry(raw_data=kwargs, table_name=table_name)

        self._update_category_cache(**fields)

        element_id = self._db.table(table_name).insert(fields)

        return element_id

    def get_entry(self, eid, table_name=None):
        """
        Get entry specified by ``eid`` in the table ``table_name`` (defaults to
        table 'standard').

        :type eid: int or str

        :raise: PeriodException if element not found
        :return: found element (tinydb.Element)
        """

        table_name = table_name or TinyDbPeriod.DEFAULT_TABLE
        element = self._db.table(table_name).get(eid=int(eid))
        if element is None:
            raise PeriodException("Element not found.")

        return element

    def update_entry(self, eid, table_name=None, **kwargs):
        """Update one or more fields of a single entry of the Period.

        :param eid: entry ID of the entry to be updated
        :param table_name: table that the entry is stored in (default:
            'standard')
        :param kwargs: 'date' for standard entries; any of 'frequency', 'start',
            'end' for recurrent entries; any of 'name', 'value', 'category' for
            either entry type
        :raise: PeriodException if element not found
        :return: ID of the updated entry
        """

        table_name = table_name or TinyDbPeriod.DEFAULT_TABLE
        fields = self._preprocess_entry(raw_data=kwargs, table_name=table_name,
                partial=True)

        self._update_category_cache(eid=eid, table_name=table_name, **fields)

        element_id = self._db.table(table_name).update(
            fields, eids=[int(eid)])[0]

        return element_id

    def _search_all_tables(self, query_impl=None):
        """Search both the standard table and the recurrent table for elements
        that satisfy the given condition.

        The elements' `eid` attribute is used as key in the returned subdicts
        because it is lost in the client-server communication protocol (on
        `financeager print`, the server calls Period.get_entries, yet the
        JSON response returned drops the Element.eid attribute s.t. it's not
        available when calling prettify on the client side).

        :param query_impl: condition for the search. If none (default), all elements are returned.
        :type query_impl: tinydb.queries.QueryImpl

        :return: dict
        """

        elements = {
                "standard": {},
                "recurrent": defaultdict(list)
                }

        if query_impl is None:
            matching_standard_elements = self._db.all()
        else:
            matching_standard_elements = self._db.search(query_impl)

        for element in matching_standard_elements:
            elements["standard"][element.eid] = element

        # all recurrent elements are generated, and the ones matching the
        # query are appended to a list that is stored under their generating
        # element's eid in the 'recurrent' subdictionary
        for element in self._db.table("recurrent").all():
            for e in self._create_recurrent_elements(element):
                matching_recurrent_element = None

                if query_impl is None:
                    matching_recurrent_element = e
                else:
                    if query_impl(e):
                        matching_recurrent_element = e

                if matching_recurrent_element is not None:
                    elements["recurrent"][element.eid].append(
                            matching_recurrent_element)

        return elements

    def _create_recurrent_elements(self, element):
        """Generate elements (holding name, value, category, date) from the
        information of the recurrent element being passed.
        """

        # parse dates to datetime objects
        start = dt.strptime(element["start"], PERIOD_DATE_FORMAT).replace(
                year=self.year)
        end = dt.strptime(element["end"], PERIOD_DATE_FORMAT).replace(year=self.year)

        now = dt.now()
        if end > now:
            # don't show entries that are in the future
            end = now

        interval = 1
        frequency = element["frequency"].upper()
        if frequency == "BIMONTHLY":
            frequency = "MONTHLY"
            interval = 2
        elif frequency == "QUARTER-YEARLY":
            frequency = "MONTHLY"
            interval = 3
        elif frequency == "HALF-YEARLY":
            frequency = "MONTHLY"
            interval = 6

        rule = rrule.rrule(getattr(rrule, frequency), dtstart=start, until=end,
                interval=interval)

        for date in rule:
            # add date description to name
            name = element["name"]
            if frequency == "MONTHLY":
                name = "{}, {}".format(name, date.strftime("%B").lower())
            elif frequency == "WEEKLY":
                name = "{}, week {}".format(name, date.strftime("%W").lower())
            elif frequency == "DAILY":
                name = "{}, day {}".format(name, date.strftime("%-j").lower())

            yield Element(dict(name=name, value=element["value"],
                category=element["category"], date=date.strftime(PERIOD_DATE_FORMAT)))

    def remove_entry(self, eid, table_name=None):
        """Remove an entry from the Period database given its ID. The category
        cache is updated.

        :param eid: ID of the element to be deleted.
        :type eid: int or str
        :param table_name: name of the table that contains the element.
            Default: TinyDbPeriod.DEFAULT_TABLE
        :type table_name: str

        :raise: PeriodException if element/ID not found.
        :return: element ID if removal was successful
        """

        table_name = table_name or TinyDbPeriod.DEFAULT_TABLE
        # might raise PeriodException if ID not existing
        entry = self.get_entry(eid=int(eid), table_name=table_name)

        self._db.table(table_name).remove(eids=[entry.eid])
        self._update_category_cache(removing=True, **entry)

        return entry.eid

    @staticmethod
    def _create_query_condition(name=None, value=None, category=None, date=None):
        condition = None
        entry = Query()

        for item_name in ["name", "value", "category", "date"]:
            item = locals()[item_name]
            if item is None:
                continue

            if isinstance(item, str):
                item = item.lower()

            # TODO use tinydb.Query.search
            new_condition = (entry[item_name].matches(".*{}.*".format(item)))
            if condition is None:
                condition = new_condition
            else:
                condition &= new_condition

        return condition

    def get_entries(self, filters=None):
        """Get dict of standard and recurrent entries that match the items of
        the filters dict, if specified. Valid keys are 'name', 'date', 'value'
        and/or 'category'.
        Constructs a condition from the given filters and uses it to query all
        tables.

        :return: dict{
                    "standard":  dict{ int: tinydb.Element },
                    "recurrent": dict{ int: list[tinydb.Element] }
                    }
        """

        filters = filters or {}
        condition = self._create_query_condition(**filters)
        return self._search_all_tables(condition)


TinyDB.DEFAULT_TABLE = TinyDbPeriod.DEFAULT_TABLE
