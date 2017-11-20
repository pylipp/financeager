# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from tinydb import database

from financeager.entries import BaseEntry, CategoryEntry
from financeager.entries import prettify as prettify_entry


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_name',
            'test_value',
            'test_date',
            'test_eid'
            ]
    suite.addTest(unittest.TestSuite(map(BaseEntryTestCase, tests)))
    tests = [
            'test_name',
            'test_value',
            'test_str'
            ]
    suite.addTest(unittest.TestSuite(map(NegativeBaseEntryTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(CategoryEntryTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(LongNegativeCategoryEntryTestCase, tests)))
    tests = [
            'test_name',
            'test_value',
            'test_str',
            'test_eid'
            ]
    suite.addTest(unittest.TestSuite(map(BaseEntryFromTinyDbElementTestCase, tests)))
    tests = [
            'test_prettify'
            ]
    suite.addTest(unittest.TestSuite(map(PrettifyBaseEntryTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(PrettifyRecurrentElementTestCase, tests)))
    return suite

class BaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.date = "2016-08-10"
        self.entry = BaseEntry(**{"name": "groceries", "value": 123.45, "date":
            self.date})

    def test_name(self):
        self.assertEqual(self.entry.name, "groceries")

    def test_value(self):
        self.assertAlmostEqual(self.entry.value, 123.45, places=5)

    def test_date(self):
        self.assertEqual(self.entry.date, self.date)

    def test_eid(self):
        self.assertEqual(self.entry.eid, 0)

class NegativeBaseEntryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = BaseEntry(**{"name": "vw bully", "value": -6000, "date":
            "01-01"})

    def test_name(self):
        self.assertEqual(self.entry.name, "vw bully")

    def test_value(self):
        self.assertEqual(self.entry.value, 6000)

    def test_str(self):
        expected = "Vw Bully".ljust(BaseEntry.NAME_LENGTH) + " " + " 6000.00 01-01"
        if BaseEntry.SHOW_EID:
            expected += "   0"
        self.assertEqual(str(self.entry), expected)

class CategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = CategoryEntry(name="gifts")

    def test_name(self):
        self.assertEqual(self.entry.name, "gifts")

    def test_value(self):
        self.assertEqual(self.entry.value, 0.0)

    def test_str(self):
        self.assertEqual(str(self.entry),
                "Gifts".ljust(CategoryEntry.NAME_LENGTH) + " " +
                "0.00".rjust(BaseEntry.VALUE_LENGTH) + " " +
                BaseEntry.DATE_LENGTH*" " +
                (BaseEntry.EID_LENGTH + 1)*" " if BaseEntry.SHOW_EID else "")

class LongNegativeCategoryEntryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = CategoryEntry(name="This is quite a LOOONG Category",
                value=-100, entries=[BaseEntry("entry", -100, "08-13")])

    def test_name(self):
        self.assertEqual(self.entry.name, "this is quite a looong category")

    def test_value(self):
        self.assertEqual(self.entry.value, 100)

    def test_str(self):
        self.assertEqual(str(self.entry),
                "This Is Quite A Lo " + "  100.00" + 6*" " + 4*" " + "\n" +
                "  Entry            " + "  100.00" + " 08-13 " + "  0")

class BaseEntryFromTinyDbElementTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "dinner for one"
        self.value = 99.9
        self.date = "12-31"
        self.eid = 1
        element = database.Element(value=dict(name=self.name, value=self.value,
            date=self.date), eid=self.eid)
        self.entry = BaseEntry.from_tinydb(element)

    def test_name(self):
        self.assertEqual(self.entry.name, "dinner for one")

    def test_value(self):
        self.assertAlmostEqual(self.entry.value, self.value, places=5)

    def test_str(self):
        self.assertEqual(str(self.entry), "Dinner For One      99.90 12-31   1")

    def test_eid(self):
        self.assertEqual(self.entry.eid, self.eid)

class PrettifyBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.element = database.Element(value=dict(
            name="soccer shoes", value=-123.45, date="04-01",
            category="sport equipment")
            )

    def test_prettify(self):
        self.assertEqual(prettify_entry(self.element), """\
Name    : Soccer Shoes
Value   : -123.45
Date    : 04-01
Category: Sport Equipment""")

class PrettifyRecurrentElementTestCase(unittest.TestCase):
    def setUp(self):
        self.element = database.Element(value=dict(
                name="retirement money", value=567.0,
                category="income", frequency="monthly", start="01-01",
                end="12-31"))

    def test_prettify(self):
        self.assertEqual(prettify_entry(self.element, True), """\
Name     : Retirement Money
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")


if __name__ == '__main__':
    unittest.main()
