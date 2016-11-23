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
            'test_default_category_in_list'
            ]
    suite.addTest(unittest.TestSuite(map(AddBaseEntryWithoutCategoryTestCase, tests)))
    tests = [
            'test_two_entries_in_list',
            'test_category_sum'
            ]
    suite.addTest(unittest.TestSuite(map(AddTwoBaseEntriesTestCase, tests)))
    tests = [
            'test_category_sum_updated'
            ]
    suite.addTest(unittest.TestSuite(map(SetValueItemTextTestCase, tests)))
    tests = [
            'test_correct_item_is_found'
            ]
    suite.addTest(unittest.TestSuite(map(FindItemByNameTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(FindItemByNameAndDateTestCase, tests)))
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

class AddBaseEntryWithoutCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.model.add_entry(BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date])))

    def test_default_category_in_list(self):
        self.assertIn(QString(CategoryItem.DEFAULT_NAME),
                self.model.category_entry_names)

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

class SetValueItemTextTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry("Aldi", self.item_a_value),
                self.item_category)
        self.model.item(0).child(0, 1).setText(
                QString("{}".format(self.item_b_value)))

    def test_category_sum_updated(self):
        self.assertAlmostEqual(self.item_b_value,
                self.model.category_sum(self.item_category), places=5)

class FindItemByNameTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.item_category = "Groceries"
        self.base_entry = BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date]))
        self.model.add_entry(self.base_entry, self.item_category)

    def test_correct_item_is_found(self):
        self.assertEqual(self.base_entry.name_item,
                self.model.find_name_item(name=self.item_name.lower(),
                    category=self.item_category))

class FindItemByNameAndDateTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_name = "Aldi"
        self.item_b_name = "Aldi"
        self.item_a_value = 66.6
        self.item_b_value = 1.00
        self.item_date = "2016-11-08"
        self.base_entry_a = BaseEntry(self.item_a_name, self.item_a_value,
            self.item_date)
        self.base_entry_b = BaseEntry(self.item_b_name, self.item_b_value)
        self.model.add_entry(self.base_entry_b)
        self.model.add_entry(self.base_entry_a)

    def test_correct_item_is_found(self):
        self.assertEqual(self.base_entry_a.name_item,
                self.model.find_name_item(name=self.item_a_name.lower(),
                    date=self.item_date))

if __name__ == '__main__':
    unittest.main()
