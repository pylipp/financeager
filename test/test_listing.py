# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager import DEFAULT_TABLE
from financeager.listing import Listing, prettify
from financeager.entries import CategoryEntry, BaseEntry


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_category_item_in_list',
    ]
    suite.addTest(unittest.TestSuite(map(AddCategoryEntryTestCase, tests)))
    tests = [
        'test_category_item_in_list',
        'test_single_item_in_list',
    ]
    suite.addTest(unittest.TestSuite(map(AddCategoryEntryTwiceTestCase, tests)))
    tests = [
        'test_str',
        'test_str_no_eid',
        'test_add_invalid_entry',
    ]
    suite.addTest(unittest.TestSuite(map(AddBaseEntryTestCase, tests)))
    tests = [
        'test_str',
    ]
    suite.addTest(unittest.TestSuite(map(AddNegativeBaseEntryTestCase, tests)))
    tests = [
        'test_sort_by_name',
        'test_sort_by_value',
    ]
    suite.addTest(unittest.TestSuite(map(SortCategoryEntriesTestCase, tests)))
    tests = [
        'test_default_category_in_list',
    ]
    suite.addTest(
        unittest.TestSuite(map(AddBaseEntryWithoutCategoryTestCase, tests)))
    tests = [
        'test_total_value',
    ]
    suite.addTest(unittest.TestSuite(map(AddTwoBaseEntriesTestCase, tests)))
    tests = [
        'test_contains_an_entry',
        'test_category_item_names',
    ]
    suite.addTest(unittest.TestSuite(map(ListingFromElementsTestCase, tests)))
    tests = [
        'test_prettify',
    ]
    suite.addTest(unittest.TestSuite(map(PrettifyListingsTestCase, tests)))
    return suite


class AddCategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.category_name = "Groceries"
        self.listing.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(),
                      self.listing.category_entry_names)


class AddCategoryEntryTwiceTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.category_name = "Groceries"
        self.listing.add_entry(CategoryEntry(name=self.category_name))
        self.listing.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(),
                      self.listing.category_entry_names)

    def test_single_item_in_list(self):
        self.assertEqual(1, len(list(self.listing.category_entry_names)))


class AddBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_str(self):
        self.assertEqual(
            str(self.listing), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date  ID ",
                "Groceries             66.60" + 10 * " ",
                "  Aldi                66.60 11-08   0"
            ]))

    def test_str_no_eid(self):
        BaseEntry.SHOW_EID = False
        self.assertEqual(
            str(self.listing),
            '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date ",
                # TODO: fix this; category entry line has to be shorter
                "Groceries             66.60          ",
                "  Aldi                66.60 11-08"
            ]))
        BaseEntry.SHOW_EID = True

    def test_add_invalid_entry(self):
        self.assertRaises(TypeError, self.listing.add_entry, None)


class SortCategoryEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        for c, v in zip("ab", [20, 10]):
            self.listing.add_entry(BaseEntry("foo", v, "01-01"), c)

    def test_sort_by_name(self):
        Listing.CATEGORY_ENTRY_SORT_KEY = "name"
        self.assertEqual(
            str(self.listing), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date  ID ",
                "A                     20.00" + 10 * " ",
                "  Foo                 20.00 01-01   0",
                "B                     10.00" + 10 * " ",
                "  Foo                 10.00 01-01   0",
            ]))

    def test_sort_by_value(self):
        Listing.CATEGORY_ENTRY_SORT_KEY = "value"
        self.assertEqual(
            str(self.listing), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date  ID ",
                "B                     10.00" + 10 * " ",
                "  Foo                 10.00 01-01   0",
                "A                     20.00" + 10 * " ",
                "  Foo                 20.00 01-01   0",
            ]))


class AddNegativeBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = -66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_str(self):
        self.assertEqual(
            str(self.listing), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date  ID ",
                "Groceries             66.60" + 10 * " ",
                "  Aldi                66.60 11-08   0"
            ]))


class AddBaseEntryWithoutCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date))

    def test_default_category_in_list(self):
        names = list(self.listing.category_entry_names)
        self.assertIn(CategoryEntry.DEFAULT_NAME, names)


class AddTwoBaseEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.date = "11-11"
        self.listing.add_entry(
            BaseEntry("Aldi", self.item_a_value, self.date), self.item_category)
        self.listing.add_entry(
            BaseEntry("Rewe", self.item_b_value, self.date), self.item_category)

    def test_total_value(self):
        self.assertAlmostEqual(
            self.item_a_value + self.item_b_value,
            self.listing.total_value(),
            places=5)


class ListingFromElementsTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "Dinner for one"
        self.value = 99.9
        self.date = "12-31"
        self.listing = Listing.from_elements(
            [dict(name=self.name, value=self.value, date=self.date, eid=0)])

    def test_contains_an_entry(self):
        self.assertIn(self.date, str(self.listing))

    def test_category_item_names(self):
        parsed_listing_entry_names = list(self.listing.category_entry_names)
        listing_entry_names = [CategoryEntry.DEFAULT_NAME]
        self.assertListEqual(listing_entry_names, parsed_listing_entry_names)


class PrettifyListingsTestCase(unittest.TestCase):
    def test_prettify_no_elements(self):
        elements = {DEFAULT_TABLE: {}, "recurrent": {}}
        self.assertEqual(prettify(elements), "")

    def test_prettify(self):
        elements = {
            DEFAULT_TABLE: {
                1: {
                    "name": "food",
                    "value": -100.01,
                    "date": "03-03",
                    "category": "groceries"
                },
                999: {
                    "name": "money",
                    "value": 299.99,
                    "date": "03-03"
                }
            },
            "recurrent": {
                42: [{
                    "name": "gold",
                    "value": 4321,
                    "date": "01-01",
                    "category": "bank"
                }]
            }
        }
        self.maxDiff = None
        elements_copy = elements.copy()
        self.assertEqual(
            prettify(elements_copy),
            "              Earnings                |               Expenses               \n"  # noqa
            "Name               Value    Date  ID  | Name               Value    Date  ID \n"  # noqa
            "Unspecified          299.99           | Groceries            100.01          \n"  # noqa
            "  Money              299.99 03-03 999 |   Food               100.01 03-03   1\n"  # noqa
            "Bank                4321.00           | \n"  # noqa
            "  Gold              4321.00 01-01  42 | \n"  # noqa
            "=============================================================================\n"  # noqa
            "Total               4620.99           | Total                100.01          "  # noqa
        )
        # Assert that original data was not modified
        self.assertDictEqual(elements, elements_copy)


if __name__ == '__main__':
    unittest.main()
