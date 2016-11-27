# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.items import (DateItem, ExpenseItem, EmptyItem, NameItem,
    ValueItem, DataItem, SumItem)
from PyQt4.QtCore import QString, QDate, QVariant


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_text_is_empty',
            'test_entry_is_none',
            'test_data_is_null'
            ]
    suite.addTest(unittest.TestSuite(map(DataItemTestCase, tests)))
    tests = [
            'test_is_not_editable'
            ]
    suite.addTest(unittest.TestSuite(map(EmptyItemTestCase, tests)))
    tests = [
            'test_text',
            'test_data',
            'test_str'
            ]
    suite.addTest(unittest.TestSuite(map(SingleWordNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(ComplexWordNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(IntegerValueItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SimpleDateItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(InvalidDateItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextDateItemTestCase, tests)))
    tests = [
            'test_text',
            'test_data'
            ]
    suite.addTest(unittest.TestSuite(map(FloatValueItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextValueItemTestCase, tests)))
    return suite


class DataItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DataItem(None)

    def test_text_is_empty(self):
        self.assertTrue(self.item.text().isEmpty())

    def test_entry_is_none(self):
        self.assertIsNone(self.item.entry)

    def test_data_is_null(self):
        self.assertTrue(self.item.data().isNull())

class EmptyItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = EmptyItem()

    def test_is_not_editable(self):
        self.assertFalse(self.item.isEditable())

class SingleWordNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("GrocErIEs")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Groceries"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("groceries"))

    def test_str(self):
        self.assertEqual(str(self.item), "groceries")

class ComplexWordNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("Miete März-Juli!")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Miete März-juli!"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("miete märz-juli!"))

    def test_str(self):
        #FIXME
        self.assertEqual(str(self.item), "miete märz-juli!")

class SetTextNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("Money")
        self.item.setText(QString("busy g3tTIn' $"))

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Busy G3ttin' $"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("busy g3ttin' $"))

    def test_str(self):
        self.assertEqual(str(self.item), "busy g3ttin' $")

class IntegerValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = ValueItem(123)

    def test_text(self):
        self.assertEqual(self.item.text(), QString("123.00"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant(123))

    def test_str(self):
        self.assertEqual(str(self.item), "123")

class FloatValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.value = 3.1415926
        self.item = ValueItem(self.value)

    def test_text(self):
        self.assertEqual(self.item.text(), QString("3.14"))

    def test_data(self):
        self.assertAlmostEqual(self.item.value, self.value, places=2)

class SetTextValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = ValueItem(42.42)
        self.item.setText(QString("13.37"))

    def test_text(self):
        self.assertEqual(self.item.text(), QString("13.37"))

    def test_data(self):
        self.assertAlmostEqual(self.item.value, 13.37, places=5)

class SimpleDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.date_str = "2016-01-01"
        self.item = DateItem(self.date_str)

    def test_text(self):
        self.assertEqual(self.item.text(), QString(self.date_str))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate(2016, 1, 1))

    def test_str(self):
        self.assertEqual(str(self.item), self.date_str)

class InvalidDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DateItem()

    def test_text(self):
        self.assertEqual(self.item.text(), QDate.currentDate().toString(DateItem.FORMAT))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate.currentDate())

    def test_str(self):
        self.assertEqual(str(self.item), unicode(
                QDate.currentDate().toString(DateItem.FORMAT)))

class SetTextDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DateItem("2016-12-24")
        self.new_date_str = "2015-11-11"
        self.item.setText(self.new_date_str)

    def test_text(self):
        self.assertEqual(self.item.text(), QString(self.new_date_str))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate(2015, 11, 11))

    def test_str(self):
        self.assertEqual(str(self.item), self.new_date_str)

if __name__ == '__main__':
    unittest.main()
