# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.items import (DateItem, ExpenseItem, EmptyItem, NameItem,
    ValueItem)
from PyQt4.QtCore import QString, QDate, QVariant


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_text_is_empty',
            'test_data_is_null',
            'test_is_not_editable'
            ]
    suite.addTest(unittest.TestSuite(map(EmptyItemTestCase, tests)))
    tests = [
            'test_text',
            'test_data'
            ]
    suite.addTest(unittest.TestSuite(map(SingleWordNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(ComplexWordNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextNameItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(IntegerValueItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(FloatValueItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextValueItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SimpleDateItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(InvalidDateItemTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(SetTextDateItemTestCase, tests)))
    return suite


class EmptyItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = EmptyItem()

    def test_text_is_empty(self):
        self.assertTrue(self.item.text().isEmpty())

    def test_data_is_null(self):
        self.assertTrue(self.item.data().isNull())

    def test_is_not_editable(self):
        self.assertFalse(self.item.isEditable())

class SingleWordNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("GrocErIEs")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Groceries"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("groceries"))

class ComplexWordNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("Miete März-Juli!")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Miete März-juli!"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("miete märz-juli!"))

class SetTextNameItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = NameItem("Money")
        self.item.setText(QString("busy g3tTIn' $"))

    def test_text(self):
        self.assertEqual(self.item.text(), QString("Busy G3ttin' $"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant("busy g3ttin' $"))

class IntegerValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = ValueItem(123)

    def test_text(self):
        self.assertEqual(self.item.text(), QString("123.00"))

    def test_data(self):
        self.assertEqual(self.item.data(), QVariant(123))

class FloatValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = ValueItem(3.1415926)

    def test_text(self):
        self.assertEqual(self.item.text(), QString("3.14"))

    #FIXME
    def test_data(self):
        self.assertEqual(self.item.data(), QVariant(3.1415926))

class SetTextValueItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = ValueItem(42.42)
        self.item.setText(QString("13.37"))

    def test_text(self):
        self.assertEqual(self.item.text(), QString("13.37"))

    #FIXME
    def test_data(self):
        self.assertEqual(self.item.data(), QVariant(13.37))

class SimpleDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DateItem("2016-01-01")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("2016-01-01"))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate(2016, 1, 1))

class InvalidDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DateItem()

    def test_text(self):
        self.assertEqual(self.item.text(), QDate.currentDate().toString(DateItem.FORMAT))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate.currentDate())

class SetTextDateItemTestCase(unittest.TestCase):
    def setUp(self):
        self.item = DateItem("2016-12-24")
        self.item.setText("2015-11-11")

    def test_text(self):
        self.assertEqual(self.item.text(), QString("2015-11-11"))

    def test_data(self):
        self.assertEqual(self.item.data(), QDate(2015, 11, 11))

if __name__ == '__main__':
    unittest.main()
