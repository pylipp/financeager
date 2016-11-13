# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt4.QtCore import QString, QDate, QVariant
from financeager.model import Model
from financeager.entries import BaseEntry


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_category_is_added',
            'test_category_sum',
            'test_item_name',
            'test_item_value',
            'test_item_date'
            ]
    suite.addTest(unittest.TestSuite(map(AddItemModelTestCase, tests)))
    return suite

class AddItemModelTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date])), self.item_category)

    def test_category_is_added(self):
        self.assertIn(self.item_category, list(self.model.categories))

    def test_category_sum(self):
        self.assertEqual(self.item_value, self.model.category_sum(self.item_category))

    def test_item_name(self):
        self.assertEqual(self.model.categories.next()[0].name, QString(self.item_name))

    def test_item_value(self):
        self.assertEqual(self.model.categories.next()[0].value, QVariant(self.item_value))

    def test_item_date(self):
        self.assertEqual(self.model.categories.next()[0].date, QDate(*self.item_date))

if __name__ == '__main__':
    unittest.main()
