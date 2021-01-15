import calendar
import datetime as dt
import json
import os.path
import tempfile
import unittest
from collections import Counter

from marshmallow import ValidationError

from financeager import (DEFAULT_POCKET_NAME, DEFAULT_TABLE, POCKET_DATE_FORMAT,
                         RECURRENT_TABLE, exceptions)
from financeager.pocket import (_DEFAULT_CATEGORY, EntryBaseSchema, Pocket,
                                RecurrentEntrySchema, StandardEntrySchema,
                                TinyDbPocket)


class Entry:
    def __init__(self, **attrs):
        self.__dict__.update(**attrs)


class CreateEmptyPocketTestCase(unittest.TestCase):
    def test_default_name(self):
        pocket = Pocket()
        self.assertEqual(pocket.name, DEFAULT_POCKET_NAME)

    def test_load_category_cache(self):
        # Create data file with one entry and load it into TinyDbPocket
        data_dir = tempfile.mkdtemp(prefix="financeager-")
        name = 1234
        with open(os.path.join(data_dir, "{}.json".format(name)), "w") as file:
            json.dump(
                {DEFAULT_TABLE: {
                    1: {
                        "name": "climbing",
                        "category": "sport"
                    }
                }}, file)
        pocket = TinyDbPocket(name=name, data_dir=data_dir)
        # Expect that 'sport' has been counted once
        self.assertEqual(pocket._category_cache["climbing"], Counter(["sport"]))
        pocket.close()


class TinyDbPocketStandardEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.pocket = TinyDbPocket(name=1901)
        self.eid = self.pocket.add_entry(
            name="Bicycle", value=-999.99, date="2020-01-01")

    @unittest.skip("missing support for leap year validation in marshmallow")
    def test_leap_year_date(self):
        eid = self.pocket.add_entry(
            name="leap win",
            value=2,
            date="02-29",
        )
        entry = self.pocket.get_entry(eid)
        self.assertEqual(entry["date"], "02-29")

    def test_get_entries(self):
        entries = self.pocket.get_entries(filters={"date": "01-"})
        self.assertEqual("bicycle", entries[DEFAULT_TABLE][1]["name"])

    def test_remove_entry(self):
        response = self.pocket.remove_entry(eid=1)
        self.assertEqual(0, len(self.pocket._db))
        self.assertEqual(1, response)

    def test_create_models_query_kwargs(self):
        eid = self.pocket.add_entry(
            name="Xmas gifts", value=500, date="2002-12-23", category="gifts")
        standard_elements = self.pocket.get_entries(
            filters={"date": "12"})[DEFAULT_TABLE]
        self.assertEqual(len(standard_elements), 1)
        self.assertEqual(standard_elements[eid]["name"], "xmas gifts")

        standard_elements = self.pocket.get_entries(
            filters={"category": None})[DEFAULT_TABLE]
        self.assertEqual(len(standard_elements), 1)

        standard_elements = self.pocket.get_entries(
            filters={"category": "gi"})[DEFAULT_TABLE]
        self.assertEqual(len(standard_elements), 1)

        self.pocket.add_entry(name="hammer", value=-33, date="2015-12-20")
        standard_elements = self.pocket.get_entries(filters={
            "name": "xmas",
            "date": "12"
        })[DEFAULT_TABLE]
        self.assertEqual(len(standard_elements), 1)
        self.assertEqual(standard_elements[eid]["name"], "xmas gifts")

    def test_category_cache(self):
        self.pocket.add_entry(
            name="walmart",
            value=-50.01,
            category="groceries",
            date="1999-02-02")
        self.pocket.add_entry(name="walmart", value=-0.99, date="1999-02-03")

        groceries_elements = self.pocket.get_entries(
            filters={"category": "groceries"})
        self.assertEqual(len(groceries_elements), 2)
        self.assertEqual(
            sum([
                e["value"] for e in groceries_elements[DEFAULT_TABLE].values()
            ]), -51)

    def test_remove_nonexisting_entry(self):
        self.assertRaises(
            exceptions.PocketEntryNotFound, self.pocket.remove_entry, eid=0)

    def test_add_remove_via_eid(self):
        entry_name = "penguin sale"
        entry_id = self.pocket.add_entry(
            name=entry_name, value=1337, date="2010-12-01")
        nr_entries = len(self.pocket._db)

        removed_entry_id = self.pocket.remove_entry(eid=entry_id)
        self.assertEqual(removed_entry_id, entry_id)
        self.assertEqual(len(self.pocket._db), nr_entries - 1)
        self.assertEqual(
            self.pocket._category_cache[entry_name][_DEFAULT_CATEGORY], 0)

    def test_get_nonexisting_entry(self):
        self.assertRaises(
            exceptions.PocketEntryNotFound, self.pocket.get_entry, eid=-1)

    def test_add_entry_default_date(self):
        name = "new backpack"
        entry_id = self.pocket.add_entry(name=name, value=-49.95, date=None)
        element = self.pocket.get_entry(entry_id)
        self.assertEqual(element["date"],
                         dt.date.today().strftime(POCKET_DATE_FORMAT))
        self.pocket.remove_entry(eid=entry_id)

    def test_update_standard_entry(self):
        self.pocket.update_entry(eid=self.eid, value=-100)
        element = self.pocket.get_entry(eid=self.eid)
        self.assertEqual(element["value"], -100)

        # kwargs with None-value should be ignored; they are passed e.g. by the
        # flask_restful RequestParser
        self.pocket.update_entry(
            eid=self.eid, name="Trekking Bicycle", value=None, category=None)
        element = self.pocket.get_entry(eid=self.eid)
        self.assertEqual(element["name"], "trekking bicycle")

        self.assertEqual(self.pocket._category_cache["bicycle"],
                         Counter({_DEFAULT_CATEGORY: 0}))
        self.assertEqual(self.pocket._category_cache["trekking bicycle"],
                         Counter({_DEFAULT_CATEGORY: 1}))

        self.pocket.update_entry(eid=self.eid, category="Sports", name=None)
        element = self.pocket.get_entry(eid=self.eid)
        self.assertEqual(element["category"], "sports")

        self.assertEqual(self.pocket._category_cache["trekking bicycle"],
                         Counter({
                             "sports": 1,
                             _DEFAULT_CATEGORY: 0
                         }))

        # string-eids should be internally converted to int
        self.pocket.update_entry(
            eid=str(self.eid), name="MTB Tandem", category="Fun", value=-1000)
        element = self.pocket.get_entry(eid=self.eid)
        self.assertEqual(element["name"], "mtb tandem")
        self.assertEqual(element["value"], -1000.0)
        self.assertEqual(element["category"], "fun")

        self.assertEqual(self.pocket._category_cache["trekking bicycle"],
                         Counter({
                             "sports": 0,
                             _DEFAULT_CATEGORY: 0
                         }))
        self.assertEqual(self.pocket._category_cache["mtb tandem"],
                         Counter({"fun": 1}))

    def test_update_nonexisting_entry(self):
        self.assertRaises(
            exceptions.PocketEntryNotFound,
            self.pocket.update_entry,
            eid=0,
            name="I shall fail")

    def test_add_invalid_entry(self):
        self.assertRaises(
            exceptions.PocketValidationFailure,
            self.pocket.add_entry,
            name="I'm invalid",
            date="1.1",
            value="hundred")

    def tearDown(self):
        self.pocket.close()


class TinyDbPocketRecurrentEntryNowTestCase(unittest.TestCase):
    def test_no_future_elements_created(self):
        # current year
        pocket = TinyDbPocket()

        elements = pocket.get_entries()
        self.assertEqual(len(elements[DEFAULT_TABLE]), 0)
        self.assertEqual(len(elements[RECURRENT_TABLE]), 0)

        today = dt.date.today().replace(year=1993)
        entry_id = pocket.add_entry(
            table_name=RECURRENT_TABLE,
            name="lunch",
            value=-5,
            frequency="daily",
            start="1993-01-01",
            end=today.strftime(POCKET_DATE_FORMAT),
        )

        day_nr = today.timetuple().tm_yday
        elements = pocket.get_entries()
        self.assertEqual(len(elements[RECURRENT_TABLE][entry_id]), day_nr)


class TinyDbPocketRecurrentEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.pocket = TinyDbPocket(name=1901)

    def test_recurrent_entries(self):
        eid = self.pocket.add_entry(
            name="rent",
            value=-500,
            table_name=RECURRENT_TABLE,
            frequency="monthly",
            start="2007-10-01",
            end="2008-11-30",
        )
        self.assertSetEqual({RECURRENT_TABLE}, self.pocket._db.tables())

        self.assertEqual(len(self.pocket._db.table(RECURRENT_TABLE).all()), 1)
        element = self.pocket._db.table(RECURRENT_TABLE).all()[0]
        recurrent_elements = list(
            self.pocket._create_recurrent_elements(element))
        self.assertEqual(len(recurrent_elements), 14)

        rep_element_names = {e["name"] for e in recurrent_elements}
        self.assertSetEqual(
            rep_element_names,
            {
                "rent, {}".format(calendar.month_name[m + 1].lower())
                for m in range(12)
            },
        )

        matching_elements = self.pocket.get_entries(
            filters={"date": "11"})[RECURRENT_TABLE]
        self.assertEqual(len(matching_elements), 1)
        self.assertEqual(matching_elements[eid][0]["name"], "rent, november")
        # the doc_id attribute is None because a new Document instance has been
        # created in Pocket._create_recurrent_elements. The 'eid' entry
        # however is 1 because the parent element is the first in the
        # recurrent table
        self.assertIsNone(matching_elements[eid][0].doc_id)

    def test_recurrent_quarter_yearly_entries(self):
        eid = self.pocket.add_entry(
            name="interest",
            value=25,
            table_name=RECURRENT_TABLE,
            frequency="quarter-yearly",
            start="1991-01-01",
            end="1991-12-31",
        )

        element = self.pocket._db.table(RECURRENT_TABLE).all()[0]
        recurrent_elements = list(
            self.pocket._create_recurrent_elements(element))
        self.assertEqual(len(recurrent_elements), 4)

        rep_element_names = {e["name"] for e in recurrent_elements}
        self.assertSetEqual(
            rep_element_names, {
                "interest, january", "interest, april", "interest, july",
                "interest, october"
            })

        recurrent_table_size = len(self.pocket._db.table(RECURRENT_TABLE))
        self.pocket.remove_entry(eid=eid, table_name=RECURRENT_TABLE)
        self.assertEqual(
            len(self.pocket._db.table(RECURRENT_TABLE)),
            recurrent_table_size - 1)

    def test_recurrent_bimonthly_entries(self):
        eid = self.pocket.add_entry(
            name="interest",
            value=25,
            table_name=RECURRENT_TABLE,
            frequency="bimonthly",
            start="2012-01-08",
            end="2012-03-08")
        recurrent_elements = self.pocket.get_entries()[RECURRENT_TABLE][eid]
        self.assertEqual(len(recurrent_elements), 2)
        self.assertEqual(recurrent_elements[0]["name"], "interest, january")

    def test_recurrent_weekly_entries(self):
        eid = self.pocket.add_entry(
            name="interest",
            value=25,
            table_name=RECURRENT_TABLE,
            frequency="weekly",
            start="2000-01-08",
            end="2000-01-14")
        recurrent_elements = self.pocket.get_entries()[RECURRENT_TABLE][eid]
        self.assertEqual(len(recurrent_elements), 1)
        self.assertEqual(recurrent_elements[0]["name"], "interest, week 01")

    def test_update_recurrent_entry(self):
        eid = self.pocket.add_entry(
            name="interest",
            value=25,
            table_name=RECURRENT_TABLE,
            frequency="quarter-yearly",
            start="2020-01-01")

        self.pocket.update_entry(
            eid=eid,
            frequency="half-yearly",
            start="2020-03-01",
            end="2020-06-30",
            table_name=RECURRENT_TABLE)

        entry = self.pocket.get_entry(eid=eid, table_name=RECURRENT_TABLE)
        self.assertEqual(entry["frequency"], "half-yearly")
        self.assertEqual(entry["start"], "2020-03-01")
        self.assertEqual(entry["end"], "2020-06-30")

        recurrent_entries = self.pocket.get_entries()[RECURRENT_TABLE][eid]
        self.assertEqual(len(recurrent_entries), 1)
        self.assertEqual(recurrent_entries[0]["date"], "2020-03-01")

        self.pocket.update_entry(
            eid=eid, value=30, frequency=None, table_name=RECURRENT_TABLE)

    def test_update_recurrent_entry_incorrectly(self):
        eid = self.pocket.add_entry(
            name="interest",
            value=25,
            table_name=RECURRENT_TABLE,
            frequency="quarter-yearly",
            start="2020-01-01")

        with self.assertRaises(exceptions.PocketValidationFailure) as context:
            self.pocket.update_entry(
                eid=eid, end="Dec-24", table_name=RECURRENT_TABLE)
        self.assertIn("end", str(context.exception))

    def test_recurrent_yearly_entry(self):
        eid = self.pocket.add_entry(
            name="Fee",
            value=-100,
            start="2015-01-01",
            end=None,
            table_name=RECURRENT_TABLE,
            frequency="yearly")
        recurrent_entries = self.pocket.get_entries()[RECURRENT_TABLE][eid]
        self.assertEqual(len(recurrent_entries), dt.date.today().year - 2014)
        self.assertEqual(recurrent_entries[0]["date"], "2015-01-01")
        self.assertEqual(recurrent_entries[0]["name"], "fee, 2015")

    def test_recurrent_entry_ending_in_future(self):
        today = dt.date.today()
        year = today.year
        eid = self.pocket.add_entry(
            name="insurance",
            value=-100,
            start="{}-01-01".format(year),
            end="{}-12-31".format(year),
            table_name=RECURRENT_TABLE,
            frequency="monthly",
        )
        recurrent_entries = self.pocket.get_entries()[RECURRENT_TABLE][eid]
        self.assertEqual(len(recurrent_entries), today.month)
        self.assertEqual(recurrent_entries[0]["date"], "{}-01-01".format(year))
        self.assertEqual(recurrent_entries[0]["name"], "insurance, january")

    def tearDown(self):
        self.pocket.close()


class ValidationTestCase(unittest.TestCase):
    def test_valid_base_entry(self):
        data = EntryBaseSchema().load({"name": "entry", "value": "5"})
        entry = Entry(**data)
        self.assertEqual(entry.name, "entry")
        self.assertEqual(entry.value, 5)
        self.assertIsNone(entry.category)

    def test_valid_base_entry_category_none(self):
        data = EntryBaseSchema().load({
            "name": "entry",
            "value": "5",
            "category": None
        })
        entry = Entry(**data)
        self.assertEqual(entry.name, "entry")
        self.assertEqual(entry.value, 5)
        self.assertIsNone(entry.category)

    def test_valid_standard_entry(self):
        data = StandardEntrySchema().load({
            "name": "entry",
            "value": 5,
            "date": "1900-05-01"
        })
        entry = Entry(**data)
        self.assertEqual(entry.date, dt.date(year=1900, month=5, day=1))

    def test_valid_standard_entry_default_date(self):
        data = StandardEntrySchema().load({"name": "entry", "value": 5})
        entry = Entry(**data)
        self.assertIsNone(entry.date)

    def test_invalid_base_entry_name(self):
        with self.assertRaises(ValidationError) as context:
            EntryBaseSchema().load({"name": "", "value": 123})
        self.assertListEqual(["name"], list(context.exception.messages.keys()))

    def test_invalid_base_entry_value(self):
        with self.assertRaises(ValidationError) as context:
            EntryBaseSchema().load({"name": "foo", "value": "hundred"})
        self.assertListEqual(["value"], list(context.exception.messages.keys()))

    def test_valid_recurrent_entry(self):
        data = RecurrentEntrySchema().load({
            "name": "rent",
            "value": -400,
            "frequency": "monthly",
            "start": "1900-01-02"
        })
        entry = Entry(**data)
        self.assertEqual(entry.frequency, "monthly")
        self.assertEqual(entry.start, dt.date(year=1900, month=1, day=2))
        self.assertEqual(entry.end, None)

    def test_invalid_recurrent_entry(self):
        with self.assertRaises(ValidationError) as context:
            RecurrentEntrySchema().load({
                "name": "rent",
                "value": -400,
                "frequency": "yaerly",
                "start": "2020-01-02"
            })
        self.assertListEqual(["frequency"],
                             list(context.exception.messages.keys()))


class ValidateEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.pocket = TinyDbPocket(name=1901)

    def test_validate_valid_standard_entry(self):
        raw_data = {"name": "MoNeY", "value": "124.5"}
        fields = self.pocket._preprocess_entry(raw_data=raw_data)

        self.assertEqual(fields["name"], "money")
        self.assertEqual(fields["value"], 124.5)
        self.assertEqual(len(fields), 4)

    def test_validate_invalid_standard_entry(self):
        raw_data = {"name": "not valid", "value": "hundred"}
        with self.assertRaises(exceptions.PocketValidationFailure) as context:
            self.pocket._preprocess_entry(raw_data=raw_data)
        self.assertIn("value", str(context.exception))

    def test_validate_valid_recurrent_entry(self):
        raw_data = {
            "name": "income",
            "value": "1111",
            "frequency": "bimonthly",
            "start": "2020-06-01"
        }
        fields = self.pocket._preprocess_entry(
            raw_data=raw_data, table_name=RECURRENT_TABLE)

        self.assertEqual(fields["frequency"], "bimonthly")
        self.assertEqual(fields["start"], raw_data["start"])
        self.assertEqual(len(fields), 6)

    def test_validate_invalid_recurrent_entry(self):
        raw_data = {
            "name": "income",
            "value": "1111",
            "frequency": "hourly",
            "start": "06-01",
            "category": ""
        }
        with self.assertRaises(exceptions.PocketValidationFailure) as context:
            self.pocket._preprocess_entry(
                raw_data=raw_data, table_name=RECURRENT_TABLE)
        self.assertIn("frequency", str(context.exception))
        self.assertIn("category", str(context.exception))

    def test_convert_fields(self):
        raw_data = {"name": "CamelCase", "value": 123.0, "category": None}
        converted_fields = self.pocket._convert_fields(**raw_data)

        # None-category is being kicked out
        self.assertEqual(len(raw_data) - 1, len(converted_fields))
        self.assertEqual(converted_fields["name"], "camelcase")
        self.assertEqual(converted_fields["value"], 123.0)

    def test_substitute_none_recurrent_fields(self):
        fields = self.pocket._substitute_none_fields(
            RECURRENT_TABLE, name="baz")
        self.assertIn("start", fields)
        self.assertIn("end", fields)
        # contains name, category, start, end
        self.assertEqual(len(fields), 4)

    def test_substitute_none_standard_fields(self):
        fields = self.pocket._substitute_none_fields(DEFAULT_TABLE, name="foo")
        self.assertIn("name", fields)
        self.assertIn("date", fields)
        # contains name, date, category
        self.assertEqual(len(fields), 3)

    def test_remove_redundant_fields(self):
        raw_data = {
            field: None
            for field in ["date", "start", "end", "frequency"]
        }
        TinyDbPocket._remove_redundant_fields(None, raw_data)
        self.assertDictEqual(raw_data, {"date": None})
        TinyDbPocket._remove_redundant_fields(RECURRENT_TABLE, raw_data)
        self.assertDictEqual(raw_data, {})

    def test_invalid_table_name(self):
        self.assertRaises(
            exceptions.PocketValidationFailure,
            self.pocket._preprocess_entry,
            table_name="unknown table")


class JsonTinyDbPocketTestCase(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.data_dir = "/tmp"
        cls.year = 1999
        cls.pocket = TinyDbPocket(name=cls.year, data_dir=cls.data_dir)
        cls.data_filepath = os.path.join(cls.data_dir,
                                         "{}.json".format(cls.year))

    def test_json_file_exists(self):
        self.assertTrue(os.path.exists(self.data_filepath))

    def test_add_get(self):
        name = "pineapple"
        eid = self.pocket.add_entry(name=name, value=-5)
        element = self.pocket.get_entry(eid=eid)
        self.assertEqual(name, element["name"])
        self.pocket.remove_entry(eid=eid)

    @classmethod
    def tearDown(cls):
        cls.pocket.close()
        os.remove(cls.data_filepath)


if __name__ == '__main__':
    unittest.main()
