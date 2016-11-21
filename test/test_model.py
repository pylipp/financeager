# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt4.QtCore import QString, QDate, QVariant
from financeager.model import Model
from financeager.entries import BaseEntry, CategoryEntry
from financeager.items import (CategoryItem, NameItem)


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_category_item_in_list'
            ]
    suite.addTest(unittest.TestSuite(map(AddCategoryEntryTestCase, tests)))
    tests = [
            'test_category_item_in_list',
            'test_single_item_in_list'
            ]
    suite.addTest(unittest.TestSuite(map(AddCategoryEntryTwiceTestCase, tests)))
    tests = [
            'test_base_entry_in_list',
            'test_category_sum'
            ]
    suite.addTest(unittest.TestSuite(map(AddBaseEntryTestCase, tests)))
    tests = [
            'test_two_entries_in_list',
            'test_category_sum'
            ]
    suite.addTest(unittest.TestSuite(map(AddTwoBaseEntriesTestCase, tests)))
    return suite

class AddCategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.category_name = "Groceries"
        self.model.add_entry(CategoryEntry(self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(CategoryItem(self.category_name).data(),
                self.model.category_entry_names)

class AddCategoryEntryTwiceTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.category_name = "Groceries"
        self.model.add_entry(CategoryEntry(self.category_name))
        self.model.add_entry(CategoryEntry(self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(CategoryItem(self.category_name).data(),
                self.model.category_entry_names)

    def test_single_item_in_list(self):
        self.assertEqual(1, len(list(self.model.category_entry_names)))

class AddBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date])), self.item_category)

    def test_base_entry_in_list(self):
        base_entry_names = [item.data() for item in
                self.model.base_entry_items("name")]
        self.assertIn(NameItem(self.item_name).data(), base_entry_names)

    def test_category_sum(self):
        self.assertAlmostEqual(self.item_value,
                self.model.category_sum(self.item_category), places=5)

class AddTwoBaseEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry("Aldi", self.item_a_value),
                self.item_category)
        self.model.add_entry(BaseEntry("Rewe", self.item_b_value),
                self.item_category)

    def test_two_entries_in_list(self):
        self.assertEqual(2, len(list(self.model.base_entry_items("name"))))

    def test_category_sum(self):
        self.assertAlmostEqual(self.item_a_value + self.item_b_value,
                self.model.category_sum(self.item_category), places=5)

if __name__ == '__main__':
    unittest.main()
