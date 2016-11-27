# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

import xml.etree.ElementTree as ET
from financeager.period import Period
from financeager.model import Model
from financeager.entries import BaseEntry
from financeager.items import CategoryItem

def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_default_name'
            ]
    suite.addTest(unittest.TestSuite(map(CreateEmptyPeriodTestCase, tests)))
    tests = [
            'test_period_name',
            'test_earnings_category_sum',
            'test_expenses_category_sum'
            ]
    suite.addTest(unittest.TestSuite(map(XmlConversionTestCase, tests)))
    return suite

class CreateEmptyPeriodTestCase(unittest.TestCase):
    def test_default_name(self):
        period = Period()
        self.assertEqual(period.name, "2016")

class XmlConversionTestCase(unittest.TestCase):
    def setUp(self):
        earnings_model = Model()
        earnings_model.add_entry(BaseEntry("Paycheck", 456.78))
        expenses_model = Model()
        # expenses_model.add_entry(BaseEntry("Citroën", 24999), category="Car")
        expenses_model.add_entry(BaseEntry("Citroen", 24999), category="Car")
        self.period = Period(models=(earnings_model, expenses_model), name="1st Quartal")
        xml_tree = self.period.convert_to_xml()
        self.parsed_period = Period(xml_tree=xml_tree)

    def test_period_name(self):
        self.assertEqual(self.parsed_period.name, "1st Quartal")

    def test_earnings_category_sum(self):
        self.assertAlmostEqual(self.parsed_period._earnings_model.category_sum(
            CategoryItem.DEFAULT_NAME), 456.78, places=5)

    def test_expenses_category_sum(self):
        self.assertAlmostEqual(self.parsed_period._expenses_model.category_sum(
            "Car"), 24999, places=5)

if __name__ == '__main__':
    unittest.main()
