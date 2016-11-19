# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt4.QtCore import QString, QDate, QVariant
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
    return suite

class BaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = BaseEntry("Groceries", 123.45, "2016-08-10")

    def test_name(self):
        self.assertEqual(self.entry.name_item.data(), QString("groceries"))

    def test_value(self):
        self.assertEqual(self.entry.value_item.data(), QVariant(123.45))

    def test_date(self):
        self.assertEqual(self.entry.date_item.data(), QDate(2016, 8, 10))

class CategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = CategoryEntry("Gifts")

    def test_name(self):
        self.assertEqual(self.entry.name_item.data(), QString("gifts"))

    def test_sum(self):
        self.assertEqual(self.entry.sum_item.data(), QVariant(0.0))

if __name__ == '__main__':
    unittest.main()
