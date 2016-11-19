# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt4.QtCore import QString, QDate, QVariant
from financeager.model import Model
from financeager.entries import BaseEntry, CategoryEntry
from financeager.items import CategoryItem


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_category_item_in_list'
            ]
    suite.addTest(unittest.TestSuite(map(AddCategoryEntryTestCase, tests)))
    tests = [
            'test_category_entry_in_list',
            'test_base_entry_in_list',
            'test_category_sum'
            ]
    # suite.addTest(unittest.TestSuite(map(AddItemModelTestCase, tests)))
    return suite

class AddCategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.category_name = "Groceries"
        self.model.add_entry(CategoryEntry(self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(CategoryItem(self.category_name).data(),
                self.model.category_entry_names)

class AddItemModelTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date])), self.item_category)

    def test_category_entry_in_list(self):
        self.assertIn(CategoryItem(self.item_category).data(),
                self.model.category_entry_names)

    def test_base_entry_in_list(self):
        base_entry_names = [item.data() for item in
                self.model.base_entry_items("name")]
        self.assertIn(QString(self.item_name), base_entry_names)

    def test_category_sum(self):
        self.assertEqual(self.item_value, self.model.category_sum(self.item_category))

if __name__ == '__main__':
    unittest.main()
