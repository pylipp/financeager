# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from PyQt5.QtCore import QDate, QVariant
import xml.etree.ElementTree as ET
from tinydb import database
from financeager.model import Model
from financeager.entries import BaseEntry, CategoryEntry
from financeager.items import (CategoryItem, NameItem)


try:
    QString = unicode
except NameError:
    # Python 3
    QString = str

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
            'test_category_sum',
            'test_str'
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
    suite.addTest(unittest.TestSuite(map(FindItemWrongCategoryTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(FindItemByNameAndDateTestCase, tests)))
    tests = [
            'test_remaining_entry',
            'test_category_sum'
            ]
    suite.addTest(unittest.TestSuite(map(RemoveEntryTestCase, tests)))
    tests = [
            'test_category_item_names',
            'test_category_sums',
            'test_base_entries'
            ]
    suite.addTest(unittest.TestSuite(map(XmlConversionTestCase, tests)))
    tests = [
            'test_contains_an_entry'
            ]
    suite.addTest(unittest.TestSuite(map(ModelFromTinyDbTestCase, tests)))
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

    def test_str(self):
        self.assertEqual(str(self.model), '\n'.join([
                "{:^38}".format("Model"),
                "Name               Value    Date" + 6*" ",
                "Groceries             66.60" + 11*" ",
                "  Aldi                66.60 2016-11-08"]))

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
                self.model.find_name_item(name=self.item_name,
                    category=self.item_category))

class FindItemWrongCategoryTestCase(unittest.TestCase):
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
        self.assertIsNone(self.model.find_name_item(name=self.item_name))

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
                self.model.find_name_item(name=self.item_a_name,
                    date=self.item_date))

class RemoveEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.base_entry_a = BaseEntry("Aldi", self.item_a_value)
        self.base_entry_b = BaseEntry("Rewe", self.item_b_value)
        self.model.add_entry(self.base_entry_a, self.item_category)
        self.model.add_entry(self.base_entry_b, self.item_category)
        self.model.remove_entry(self.base_entry_a, category=self.item_category)

    def test_remaining_entry(self):
        self.assertEqual(list(self.model.base_entry_items("name"))[0],
                self.base_entry_b.name_item)

    def test_category_sum(self):
        self.assertAlmostEqual(self.model.category_sum(self.item_category),
                self.item_b_value, places=5)

class XmlConversionTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = (2016, 11, 8)
        self.item_category = "Groceries"
        self.model.add_entry(BaseEntry(self.item_name, self.item_value,
            "-".join([str(s) for s in self.item_date])), self.item_category)
        model_element = self.model.convert_to_xml()
        output = ET.tostring(model_element, "utf-8")
        parsed_input = ET.fromstring(output)
        self.parsed_model = Model(parsed_input)

    def test_category_item_names(self):
        model_entry_names = list(self.model.category_entry_names)
        parsed_model_entry_names = list(self.parsed_model.category_entry_names)
        self.assertListEqual(model_entry_names, parsed_model_entry_names)

    def test_category_sums(self):
        self.assertAlmostEqual(
                self.model.category_sum(self.item_category),
                self.parsed_model.category_sum(self.item_category), places=5)

    def test_base_entries(self):
        item = self.model.find_name_item(name=self.item_name,
                category=self.item_category)
        parsed_item = self.parsed_model.find_name_item(name=self.item_name,
                category=self.item_category)
        self.assertCountEqual(
                [str(i) for i in item.entry.items],
                [str(i) for i in parsed_item.entry.items])

class ModelFromTinyDbTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "Dinner for one"
        self.value = 99.9
        self.date = "2016-12-31"
        element = database.Element(value=dict(name=self.name, value=self.value,
            date=self.date))
        self.model = Model.from_tinydb([element])

    def test_contains_an_entry(self):
        self.assertIsNotNone(self.model.find_name_item(date=self.date))

if __name__ == '__main__':
    unittest.main()
