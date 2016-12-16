# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt4.QtCore import QString, QDate, QVariant
from tinydb import database
from financeager.entries import BaseEntry, CategoryEntry


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_name',
            'test_value',
            'test_date'
            ]
    suite.addTest(unittest.TestSuite(map(BaseEntryTestCase, tests)))
    tests = [
            'test_name',
            'test_sum'
            ]
    suite.addTest(unittest.TestSuite(map(CategoryEntryTestCase, tests)))
    tests = [
            'test_name',
            'test_value',
            'test_str'
            ]
    suite.addTest(unittest.TestSuite(map(BaseEntryFromTinyDbElementTestCase, tests)))
    return suite

class BaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = BaseEntry("Groceries", 123.45, "2016-08-10")

    def test_name(self):
        self.assertEqual(self.entry.name_item.data(), QString("groceries"))

    def test_value(self):
        self.assertAlmostEqual(self.entry.value_item.value, 123.45, places=5)

    def test_date(self):
        self.assertEqual(self.entry.date_item.data(), QDate(2016, 8, 10))

class CategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = CategoryEntry("Gifts")

    def test_name(self):
        self.assertEqual(self.entry.name_item.data(), QString("gifts"))

    def test_sum(self):
        self.assertEqual(self.entry.sum_item.data(), QVariant(0.0))

class BaseEntryFromTinyDbElementTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "Dinner for one"
        self.value = 99.9
        self.date = "2016-12-31"
        element = database.Element(value=dict(name=self.name, value=self.value,
            date=self.date))
        self.entry = BaseEntry.from_tinydb_element(element)

    def test_name(self):
        self.assertEqual(str(self.entry.name_item), "dinner for one")

    def test_value(self):
        self.assertAlmostEqual(self.entry.value_item.value, self.value, places=5)

    def test_str(self):
        self.assertEqual(str(self.entry), "Dinner For One    99.90 2016-12-31")

if __name__ == '__main__':
    unittest.main()
