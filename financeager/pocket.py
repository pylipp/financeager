"""Defines Pocket database object holding per-year financial data."""

import os.path
from collections import Counter, defaultdict
from datetime import datetime as dt

from dateutil import rrule
from marshmallow import Schema, ValidationError, fields, validate
from tinydb import Query, TinyDB, storages
from tinydb.database import Document

from . import (
    DEFAULT_POCKET_NAME,
    DEFAULT_TABLE,
    POCKET_DATE_FORMAT,
    RECURRENT_TABLE,
    UNSET_INDICATOR,
    exceptions,
)

_DEFAULT_CATEGORY = None
FREQUENCY_CHOICES = [
    "yearly",
    "half-yearly",
    "quarter-yearly",
    "bimonthly",
    "monthly",
    "weekly",
    "daily",
]


class EntryBaseSchema(Schema):
    name = fields.String(
        required=True, validate=validate.Length(min=1), allow_none=True
    )
    value = fields.Float(required=True, allow_none=True)
    category = fields.String(validate=validate.Length(min=1), missing=None)


class StandardEntrySchema(EntryBaseSchema):
    date = fields.Date(format=POCKET_DATE_FORMAT, missing=None)


class RecurrentEntrySchema(EntryBaseSchema):
    frequency = fields.String(
        validate=validate.OneOf(choices=FREQUENCY_CHOICES),
        required=True,
        allow_none=True,
    )
    start = fields.Date(format=POCKET_DATE_FORMAT, missing=None)
    end = fields.Date(format=POCKET_DATE_FORMAT, missing=None)


class Pocket:
    def __init__(self, name=None):
        """Create Pocket object. Its name defaults to the current year if not
        specified.
        """
        self._name = f"{name or DEFAULT_POCKET_NAME}"

    @property
    def name(self):
        return self._name


class TinyDbPocket(Pocket):
    def __init__(self, name=None, data_dir=None, **kwargs):
        """Create a pocket with a TinyDB database backend, identified by 'name'.
        If 'data_dir' is given, the database storage type is JSON (the storage
        filepath is derived from the Pocket's name). Otherwise the data is
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
            args = [os.path.join(data_dir, f"{self.name}.json")]
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

        :raise: PocketValidationFailure if validation failed or table name
            unknown
        """

        table_name = table_name or DEFAULT_TABLE
        if table_name not in [RECURRENT_TABLE, DEFAULT_TABLE]:
            raise exceptions.PocketValidationFailure(
                f"Unknown table name: {table_name}"
            )

        self._remove_redundant_fields(table_name, raw_data)

        validated_fields = self._validate_entry(
            raw_data=raw_data, table_name=table_name, partial=partial
        )
        converted_fields = self._convert_fields(**validated_fields)

        if not partial:
            converted_fields = self._substitute_none_fields(
                table_name=table_name, **converted_fields
            )

        return converted_fields

    @staticmethod
    def _remove_redundant_fields(table_name, raw_data):
        """The raw data (e.g. parsed from the command line) might contain fields
        that are not required by the given table type and hence, they crash the
        schematics validation ('Rogue field' error). This method removes
        redundant fields in `raw_data` in-place.
        """

        if table_name == RECURRENT_TABLE:
            redundant_fields = ["date"]
        else:
            redundant_fields = ["start", "end", "frequency"]

        for field in redundant_fields:
            raw_data.pop(field, None)

    @staticmethod
    def _validate_entry(raw_data, table_name, **schema_kwargs):
        """Validate raw entry data acc. to ValidationSchema.

        :return: primitive (type-correct) representation of fields
        :raise: PocketValidationFailure if validation failed
        """

        ValidationSchema = (
            RecurrentEntrySchema
            if table_name == RECURRENT_TABLE
            else StandardEntrySchema
        )

        try:
            schema = ValidationSchema(**schema_kwargs)
            validated_data = schema.load(raw_data)
            return schema.dump(validated_data)
        except ValidationError as e:
            infos = [
                f"{field}: {'; '.join(messages)}"
                for field, messages in e.messages.items()
            ]
            raise exceptions.PocketValidationFailure(
                "Invalid input data:\n{}".format("\n".join(infos))
            )

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

        # table_name is either of two values; verified in _preprocess_entry
        if table_name == RECURRENT_TABLE:
            if fields.get("start") is None:
                substituted_fields["start"] = dt.today().strftime(POCKET_DATE_FORMAT)
            if fields.get("end") is None:
                substituted_fields["end"] = None
        else:
            if fields.get("date") is None:
                substituted_fields["date"] = dt.today().strftime(POCKET_DATE_FORMAT)

        if fields.get("category") is None:
            name = fields["name"]

            # Find the most common categories previously assigned for the given
            # name. If there is only one OR if there is one that is used more
            # often than any other, assign it; otherwise default to None
            category = _DEFAULT_CATEGORY
            most_common_categories = self._category_cache[name].most_common(2)
            nr_most_common_categories = len(most_common_categories)

            if nr_most_common_categories == 1 or (
                nr_most_common_categories > 1
                and most_common_categories[0][1] != most_common_categories[1][1]
            ):
                category = most_common_categories[0][0]

            substituted_fields["category"] = category

        return substituted_fields

    def _update_category_cache(
        self, eid=None, table_name=None, removing=False, **fields
    ):
        """Update the category cache when adding or updating an entry. The `eid`
        kwarg is used to distinguish the use cases.

        :param eid: element ID when updating
        :param table_name: table name when updating
        :param removing: indicate updating cache after removing an entry
        :param fields: preprossed entry fields to be inserted in the database

        :raise: PocketEntryNotFound if element not found when updating
        """

        if eid is None:
            name = fields["name"]
            category = fields["category"]
            if removing:
                self._category_cache[name][category] -= 1
            else:
                self._category_cache[name].update([category])
        else:
            # raises a PocketEntryNotFound if eid is not found
            old_entry = self.get_entry(eid=eid, table_name=table_name)
            old_name = old_entry["name"]
            old_category = old_entry["category"]

            # update category cache if one of name or category was changed
            if fields.get("name") is not None or fields.get("category") is not None:
                self._category_cache[old_name][old_category] -= 1
                self._category_cache[fields.get("name") or old_name][
                    fields.get("category") or old_category
                ] += 1

    def add_entry(self, table_name=None, **kwargs):
        """
        Add an entry (standard or recurrent) to the database.
        If 'table_name' is not specified, the kwargs name, value[, category,
        date] are used to insert a unique entry in the standard table.
        With 'table_name' as 'recurrent', the kwargs name, value, frequency
        [, start, end, category] are used to insert a template entry in the
        recurrent table.

        Two kwargs are mandatory:
            :param name: entry name
            :type name: str
            :param value: entry value
            :type value: float, int or str

        The following kwarg is optional:
            :param category: entry category. If not specified, the program
                attempts to derive it from previous, eponymous entries. If this
                fails, ``_DEFAULT_CATEGORY`` is assigned
            :type category: str or None

        The following kwarg is optional for standard entries:
            :param date: entry date. Defaults to current date
            :type date: str of ``POCKET_DATE_FORMAT``

        The following kwarg is mandatory for recurrent entries:
            :param frequency: 'yearly', 'half-yearly', 'quarter-yearly',
                'bimonthly', 'monthly', 'weekly' or 'daily'

        The following kwargs are optional for recurrent entries:
            :param start: start date (defaults to current date)
            :param end: end date (defaults to None which evaluates to the
                current day when the entry is queried)

        :raise: PocketValidationFailure if validation failed
        :return: TinyDB ID of new entry (int)
        """

        table_name = table_name or DEFAULT_TABLE
        fields = self._preprocess_entry(raw_data=kwargs, table_name=table_name)

        self._update_category_cache(**fields)

        element_id = self._db.table(table_name).insert(fields)

        return element_id

    def get_entry(self, eid, table_name=None):
        """
        Get entry specified by ``eid`` in the table ``table_name`` (defaults to
        table 'standard').

        :type eid: int or str

        :raise: PocketEntryNotFound if element not found
        :return: found element (tinydb.Document)
        """

        table_name = table_name or DEFAULT_TABLE
        element = self._db.table(table_name).get(doc_id=int(eid))
        if element is None:
            raise exceptions.PocketEntryNotFound("Entry not found.")

        return element

    def _preprocess_entry_for_update(self, *, table_name, raw_data):
        """Handle special case for unsetting 'category' and/or 'end' fields while
        preprocessing the entry.
        """
        # Skip field for validation if indicator value present
        end = raw_data.get("end")
        if end == UNSET_INDICATOR:
            del raw_data["end"]
        category = raw_data.get("category")
        if category == UNSET_INDICATOR:
            del raw_data["category"]

        fields = self._preprocess_entry(
            raw_data=raw_data, table_name=table_name, partial=True
        )

        # Unset fields
        if end == UNSET_INDICATOR:
            fields["end"] = None
        if category == UNSET_INDICATOR:
            fields["category"] = None

        return fields

    def update_entry(self, eid, table_name=None, **kwargs):
        """Update one or more fields of a single entry of the Pocket.

        :param eid: entry ID of the entry to be updated
        :param table_name: table that the entry is stored in (default:
            'standard')
        :param kwargs: 'date' for standard entries; any of 'frequency', 'start',
            'end' for recurrent entries; any of 'name', 'value', 'category' for
            either entry type
        :raise: PocketEntryNotFound if element not found
        :return: ID of the updated entry
        """

        table_name = table_name or DEFAULT_TABLE
        fields = self._preprocess_entry_for_update(
            raw_data=kwargs, table_name=table_name
        )

        self._update_category_cache(eid=eid, table_name=table_name, **fields)

        element_id = self._db.table(table_name).update(fields, doc_ids=[int(eid)])[0]

        return element_id

    def _search_all_tables(self, condition):
        """Search both the standard table and the recurrent table for elements
        that satisfy the given condition.

        The entries' `doc_id` attribute is used as key in the returned subdicts
        because it is lost in the client-server communication protocol (on
        `financeager print`, the server calls Pocket.get_entries, yet the
        JSON response returned drops the Document.doc_id attribute s.t. it's not
        available when calling prettify on the client side).

        :param condition: condition for the search
        :type condition: tinydb.queries.QueryInstance

        :return: dict
        """

        elements = {DEFAULT_TABLE: {}, RECURRENT_TABLE: defaultdict(list)}

        for element in self._db.search(condition):
            elements[DEFAULT_TABLE][element.doc_id] = element

        # all recurrent elements are generated, and the ones matching the
        # condition are appended to a list that is stored under their generating
        # element's doc_id in the 'recurrent' subdictionary
        for element in self._db.table(RECURRENT_TABLE).all():
            for e in self._create_recurrent_elements(element):
                if condition(e):
                    elements[RECURRENT_TABLE][element.doc_id].append(e)

        return elements

    def _create_recurrent_elements(self, element):
        """Generate elements (holding name, value, category, date) from the
        information of the recurrent element being passed.
        """

        # parse dates to datetime objects
        start = dt.strptime(element["start"], POCKET_DATE_FORMAT)
        now = dt.now()
        end = element["end"]
        end = now if end is None else dt.strptime(end, POCKET_DATE_FORMAT)

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

        rule = rrule.rrule(
            getattr(rrule, frequency), dtstart=start, until=end, interval=interval
        )

        for date in rule:
            # add date description to name
            name = element["name"]
            if frequency == "YEARLY":
                name = f"{name}, {date.strftime('%Y')}"
            elif frequency == "MONTHLY":
                name = f"{name}, {date.strftime('%B').lower()}"
            elif frequency == "WEEKLY":
                name = f"{name}, week {date.strftime('%W').lower()}"
            else:  # DAILY
                name = f"{name}, day {date.strftime('%-j').lower()}"

            yield Document(
                doc_id=None,
                value=dict(
                    name=name,
                    value=element["value"],
                    category=element["category"],
                    date=date.strftime(POCKET_DATE_FORMAT),
                ),
            )

    def remove_entry(self, eid, table_name=None):
        """Remove an entry from the Pocket database given its ID. The category
        cache is updated.

        :param eid: ID of the element to be deleted.
        :type eid: int or str
        :param table_name: name of the table that contains the element.
            Default: 'standard'
        :type table_name: str

        :raise: PocketEntryNotFound if element/ID not found.
        :return: element ID if removal was successful
        """

        table_name = table_name or DEFAULT_TABLE
        # might raise PocketEntryNotFound if ID not existing
        entry = self.get_entry(eid=int(eid), table_name=table_name)

        self._db.table(table_name).remove(doc_ids=[entry.doc_id])
        self._update_category_cache(removing=True, **entry)

        return entry.doc_id

    @staticmethod
    def _create_query_condition(**filters):
        """Construct query condition according to given filters. A filter is
        given by a key-value pair. The key indicates the field, the value the
        pattern to filter for. Valid keys are 'name', 'date', 'value' and/or
        'category'. Patterns must be of type string, or None (only for the fields
        'category' and 'end; indicates filtering for all entries of the default
        category, and recurrent entries with indefinite end, resp.).
        :return: tinydb.queries.QueryInstance (default: noop)
        """
        condition = Query().noop()
        if not filters:
            return condition

        entry = Query()
        for field, pattern in filters.items():
            if pattern is None and field in ["category", "end"]:
                # The 'category' and 'end' fields are of type string or None. The
                # condition is constructed depending on the filter pattern
                new_condition = entry[field] == None  # noqa
            elif field == "value":
                new_condition = entry[field] == float(pattern)
            else:
                new_condition = entry[field].search(pattern.lower())

            condition &= new_condition

        return condition

    def get_entries(self, filters=None, recurrent_only=False):
        """Get dict of standard and recurrent entries that match the items of
        the filters dict, if specified. Constructs a condition from the given
        filters and uses it to query all tables.
        If `recurrent_only` is true, return a list of all entries of the
        recurrent table. Filters are applied.

        :return: dict{
                    DEFAULT_TABLE:  dict{ int: tinydb.Document },
                    RECURRENT_TABLE: dict{ int: list[tinydb.Document] }
                    } or
                 list[tinydb.Document]
        """
        filters = filters or {}
        condition = self._create_query_condition(**filters)

        if recurrent_only:
            # Flatten tinydb Document into dict
            return [
                {**e, **{"eid": e.doc_id}}
                for e in self._db.table(RECURRENT_TABLE).search(condition)
            ]

        return self._search_all_tables(condition)

    def get_categories(self):
        """Return unique category names of the default table in alphabetical order."""
        category_names = set(e["category"] for e in self._db.table(DEFAULT_TABLE).all())
        category_names.discard(_DEFAULT_CATEGORY)
        return sorted(category_names)

    def close(self):
        """Close underlying database."""
        self._db.close()


TinyDB.default_table_name = DEFAULT_TABLE
