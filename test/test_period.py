# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from tinydb import database, Query, storages
from financeager.period import TinyDbPeriod, PeriodException
from financeager.model import Model
from financeager.entries import CategoryEntry
from financeager.config import CONFIG
from datetime import datetime as dt
import os
from collections import Counter

def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_default_name'
            ]
    suite.addTest(unittest.TestSuite(map(CreateEmptyPeriodTestCase, tests)))
    tests = [
            'test_get_entries',
            'test_remove_entry',
            'test_create_models_query_kwargs',
            'test_category_cache',
            'test_remove_nonexisting_entry'
            ,'test_add_rm_via_eid'
            ,'test_get_nonexisting_entry',
            'test_update_standard_entry'
            ]
    suite.addTest(unittest.TestSuite(map(TinyDbPeriodStandardEntryTestCase, tests)))
    tests = [
            'test_recurrent_entries',
            'test_recurrent_quarter_yearly_entries',
            'test_update_recurrent_entry'
            ]
    suite.addTest(unittest.TestSuite(map(TinyDbPeriodRecurrentEntryTestCase, tests)))
    return suite

class CreateEmptyPeriodTestCase(unittest.TestCase):
    def test_default_name(self):
        period = TinyDbPeriod()
        self.assertEqual(period.name, "2017")
        period.close()

class TinyDbPeriodStandardEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.period = TinyDbPeriod(name=1901, storage=storages.MemoryStorage)
        self.eid = self.period.add_entry(name="Bicycle", value=-999.99,
                date="1901-01-01")

    def test_get_entries(self):
        self.assertIsInstance(
                self.period.get_entries(name="Bicycle")["standard"][1],
                database.Element)

    def test_remove_entry(self):
        response = self.period.remove_entry(eid=1)
        self.assertEqual(0, len(self.period))
        self.assertEqual(1, response)

    def test_create_models_query_kwargs(self):
        eid = self.period.add_entry(name="Xmas gifts", value=500, date="1901-12-23")
        standard_elements = self.period.get_entries(date="1901-12")["standard"]
        self.assertEqual(len(standard_elements), 1)
        self.assertEqual(standard_elements[eid]["name"], "xmas gifts")

        model = Model.from_tinydb(standard_elements.values())
        self.assertEqual(model.categories[0].entries[0].eid, eid)

        self.period.add_entry(name="hammer", value=-33, date="1901-12-20")
        standard_elements = self.period.get_entries(
                name="xmas", date="1901-12")["standard"]
        self.assertEqual(len(standard_elements), 1)
        self.assertEqual(standard_elements[eid]["name"], "xmas gifts")

    def test_category_cache(self):
        self.period.add_entry(name="walmart", value=-50.01,
                category="groceries", date="1901-02-02")
        self.period.add_entry(name="walmart", value=-0.99, date="1901-02-03")

        groceries_elements = self.period.get_entries(category="groceries")
        self.assertEqual(len(groceries_elements), 2)
        self.assertEqual(sum([e["value"] for e in
            groceries_elements["standard"].values()]), -51)

    def test_remove_nonexisting_entry(self):
        self.assertRaises(PeriodException, self.period.remove_entry, eid=0)
        self.assertRaises(PeriodException, self.period.remove_entry, eid=None)

    def test_add_rm_via_eid(self):
        entry_name = "penguin sale"
        entry_id = self.period.add_entry(name=entry_name, value=1337,
                date="1901-12-01")
        nr_entries = len(self.period)

        removed_entry_id = self.period.remove_entry(eid=entry_id)
        self.assertEqual(removed_entry_id, entry_id)
        self.assertEqual(len(self.period), nr_entries - 1)
        self.assertEqual(self.period._category_cache[entry_name]["unspecified"], 0)

    def test_get_nonexisting_entry(self):
        self.assertRaises(PeriodException, self.period.get_entry, eid=-1)

    def test_add_entry_default_date(self):
        name = "new backpack"
        entry_id = self.period.add_entry(name=name, value=-49.95)
        element = self.period.get_entry(entry_id)
        self.assertEqual(element["date"], dt.today().strftime(
            CONFIG["DATABASE"]["date_format"]))
        self.period.remove_entry(eid=entry_id)

    def test_update_standard_entry(self):
        self.period.update_entry(eid=self.eid, value=-100)
        element = self.period.get_entry(eid=self.eid)
        self.assertEqual(element["value"], -100)

        self.period.update_entry(eid=self.eid, name="Trekking Bicycle")
        element = self.period.get_entry(eid=self.eid)
        self.assertEqual(element["name"], "trekking bicycle")

        self.assertEqual(self.period._category_cache["bicycle"],
                Counter({"unspecified": 0}))
        self.assertEqual(self.period._category_cache["trekking bicycle"],
                Counter({"unspecified": 1}))

        self.period.update_entry(eid=self.eid, category="Sports")
        element = self.period.get_entry(eid=self.eid)
        self.assertEqual(element["category"], "sports")

        self.assertEqual(self.period._category_cache["trekking bicycle"],
                Counter({"sports": 1, "unspecified": 0}))

        self.period.update_entry(eid=self.eid, name="MTB Tandem",
                category="Fun", value=-1000)
        element = self.period.get_entry(eid=self.eid)
        self.assertEqual(element["name"], "mtb tandem")
        self.assertEqual(element["value"], -1000.0)
        self.assertEqual(element["category"], "fun")

        self.assertEqual(self.period._category_cache["trekking bicycle"],
                Counter({"sports": 0, "unspecified": 0}))
        self.assertEqual(self.period._category_cache["mtb tandem"],
                Counter({"fun": 1}))

    def tearDown(self):
        self.period.close()

class TinyDbPeriodRecurrentEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.period = TinyDbPeriod(name=1901, storage=storages.MemoryStorage)

    def test_recurrent_entries(self):
        eid = self.period.add_entry(name="rent", value=-500,
                table_name="recurrent", frequency="monthly", start="10-01")
        self.assertSetEqual({"standard", "recurrent"}, self.period.tables())

        self.assertEqual(len(self.period.table("recurrent").all()), 1)
        element = self.period.table("recurrent").all()[0]
        recurrent_elements = list(self.period._create_recurrent_elements(element))
        self.assertEqual(len(recurrent_elements), 3)

        rep_element_names = {e["name"] for e in recurrent_elements}
        self.assertSetEqual(rep_element_names,
                {"rent october", "rent november", "rent december"})

        matching_elements = self.period.get_entries(date="11")["recurrent"]
        self.assertEqual(len(matching_elements), 1)
        self.assertEqual(
                matching_elements[eid][0]["name"], "rent november")
        # the eid attribute is None because a new Element instance has been
        # created in Period._create_recurrent_elements. The 'eid' entry
        # however is 1 because the parent element is the first in the
        # "recurrent" table
        self.assertIsNone(matching_elements[eid][0].eid)

    def test_recurrent_quarter_yearly_entries(self):
        eid = self.period.add_entry(name="interest", value=25,
                table_name="recurrent", frequency="quarter-yearly",
                start="01-01")

        element = self.period.table("recurrent").all()[0]
        recurrent_elements = list(self.period._create_recurrent_elements(element))
        self.assertEqual(len(recurrent_elements), 4)

        rep_element_names = {e["name"] for e in recurrent_elements}
        self.assertSetEqual(rep_element_names,
                {"interest january", "interest april", "interest july", "interest october"})

        recurrent_table_size = len(self.period.table("recurrent"))
        self.period.remove_entry(eid=eid, table_name="recurrent")
        self.assertEqual(len(self.period.table("recurrent")),
                recurrent_table_size - 1)

    def test_update_recurrent_entry(self):
        eid = self.period.add_entry(name="interest", value=25,
                table_name="recurrent", frequency="quarter-yearly",
                start="01-01")

        self.period.update_entry(eid=eid, frequency="half-yearly",
                start="03-01", end="06-30", table_name="recurrent")

        entry = self.period.get_entry(eid=eid, table_name="recurrent")
        self.assertEqual(entry["frequency"], "half-yearly")
        self.assertEqual(entry["start"], "03-01")
        self.assertEqual(entry["end"], "06-30")

        recurrent_entries = self.period.get_entries()["recurrent"][eid]
        self.assertEqual(len(recurrent_entries), 1)
        self.assertEqual(recurrent_entries[0]["date"], "03-01")

    def tearDown(self):
        self.period.close()

if __name__ == '__main__':
    unittest.main()
