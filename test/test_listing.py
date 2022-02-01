import unittest

from financeager import DEFAULT_TABLE, RECURRENT_TABLE
from financeager.entries import BaseEntry, CategoryEntry
from financeager.listing import Listing, _derive_listings, prettify


class AddCategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.category_name = "Groceries"
        self.listing.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(), self.listing.category_entry_names)


class AddCategoryEntryTwiceTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.category_name = "Groceries"
        self.listing.add_entry(CategoryEntry(name=self.category_name))
        self.listing.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(), self.listing.category_entry_names)

    def test_single_item_in_list(self):
        self.assertEqual(1, len(list(self.listing.category_entry_names)))


class AddBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "2000-11-08"
        self.item_category = "groceries"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category,
        )

    def test_str(self):
        category_entry = self.listing.categories[0]
        self.assertEqual(category_entry.name, self.item_category)
        self.assertEqual(len(category_entry.entries), 1)

    def test_add_invalid_entry(self):
        self.assertRaises(TypeError, self.listing.add_entry, None)


class AddBaseEntryWithoutCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "2009-11-08"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            category_name=CategoryEntry.DEFAULT_NAME,
        )

    def test_default_category_in_list(self):
        names = list(self.listing.category_entry_names)
        self.assertIn(CategoryEntry.DEFAULT_NAME, names)


class AddTwoBaseEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.date = "2008-11-11"
        self.listing.add_entry(
            BaseEntry("Aldi", self.item_a_value, self.date), self.item_category
        )
        self.listing.add_entry(
            BaseEntry("Rewe", self.item_b_value, self.date), self.item_category
        )

    def test_total_value(self):
        self.assertAlmostEqual(
            self.item_a_value + self.item_b_value, self.listing.total_value(), places=5
        )


class ListingFromElementsTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "Dinner for one"
        self.value = 99.9
        self.date = "1980-12-31"
        self.listing = Listing.from_elements(
            [dict(name=self.name, value=self.value, date=self.date, eid=0)],
            default_category=CategoryEntry.DEFAULT_NAME,
        )

    def test_contains_an_entry(self):
        self.assertEqual(self.date[2:], self.listing.categories[0].entries[0].date)

    def test_category_item_names(self):
        parsed_listing_entry_names = list(self.listing.category_entry_names)
        listing_entry_names = [CategoryEntry.DEFAULT_NAME]
        self.assertListEqual(listing_entry_names, parsed_listing_entry_names)


class PrettifyListingsTestCase(unittest.TestCase):
    def test_prettify_no_elements(self):
        elements = {DEFAULT_TABLE: {}, RECURRENT_TABLE: {}}
        self.assertEqual(prettify(elements), "No entries found.")

    def test_derive_listings(self):
        expense = {
            "name": "food",
            "value": -100.01,
            "date": "2000-03-03",
            "category": "groceries",
        }
        earning = {"name": "money", "value": 299.99, "date": "2000-03-03"}
        recurrent_earning = {
            "name": "gold",
            "value": 4321,
            "date": "2000-01-01",
            "category": "bank",
        }
        elements = {
            DEFAULT_TABLE: {
                1: expense,
                999: earning,
            },
            RECURRENT_TABLE: {42: [recurrent_earning]},
        }
        listing_earnings, listing_expenses = _derive_listings(
            elements, default_category=CategoryEntry.DEFAULT_NAME
        )
        self.assertEqual(listing_earnings.name, "Earnings")
        self.assertEqual(len(listing_earnings.categories), 2)
        for category in listing_earnings.categories:
            self.assertEqual(len(category.entries), 1)
        self.assertEqual(listing_expenses.name, "Expenses")
        self.assertEqual(len(listing_expenses.categories), 1)
        for category in listing_expenses.categories:
            self.assertEqual(len(category.entries), 1)


if __name__ == "__main__":
    unittest.main()
