import unittest

from financeager import DEFAULT_TABLE, RECURRENT_TABLE
from financeager.entries import BaseEntry, CategoryEntry
from financeager.listing import Listing, prettify


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
        self.item_date = "2000-11-08"
        self.item_category = "Groceries"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_str(self):
        self.assertEqual(
            self.listing.prettify(), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date     ID  ",
                "Groceries             66.60" + 14 * " ",
                "  Aldi                66.60 00-11-08    0"
            ]))

    def test_str_no_eid(self):
        BaseEntry.SHOW_EID = False
        self.assertEqual(
            self.listing.prettify(),
            '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date    ",
                # TODO: fix this; category entry line has to be shorter
                "Groceries             66.60              ",
                "  Aldi                66.60 00-11-08"
            ]))
        BaseEntry.SHOW_EID = True

    def test_add_invalid_entry(self):
        self.assertRaises(TypeError, self.listing.add_entry, None)


class SortCategoryEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        for c, v in zip("ab", [20, 10]):
            self.listing.add_entry(BaseEntry("foo", v, "2000-01-01"), c)

    def test_sort_by_name(self):
        self.assertEqual(
            self.listing.prettify(category_sort="name"), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date     ID  ",
                "A                     20.00" + 14 * " ",
                "  Foo                 20.00 00-01-01    0",
                "B                     10.00" + 14 * " ",
                "  Foo                 10.00 00-01-01    0",
            ]))

    def test_sort_by_value(self):
        self.assertEqual(
            self.listing.prettify(), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date     ID  ",
                "B                     10.00" + 14 * " ",
                "  Foo                 10.00 00-01-01    0",
                "A                     20.00" + 14 * " ",
                "  Foo                 20.00 00-01-01    0",
            ]))


class AddNegativeBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = -66.6
        self.item_date = "2000-11-08"
        self.item_category = "Groceries"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_str(self):
        self.assertEqual(
            self.listing.prettify(), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Listing"),
                "Name               Value    Date     ID  ",
                "Groceries             66.60" + 14 * " ",
                "  Aldi                66.60 00-11-08    0"
            ]))


class AddBaseEntryWithoutCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.listing = Listing()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "2009-11-08"
        self.listing.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            category_name=CategoryEntry.DEFAULT_NAME)

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
        self.date = "1980-12-31"
        self.listing = Listing.from_elements(
            [dict(name=self.name, value=self.value, date=self.date, eid=0)],
            default_category=CategoryEntry.DEFAULT_NAME)

    def test_contains_an_entry(self):
        self.assertIn(self.date[2:], self.listing.prettify())

    def test_category_item_names(self):
        parsed_listing_entry_names = list(self.listing.category_entry_names)
        listing_entry_names = [CategoryEntry.DEFAULT_NAME]
        self.assertListEqual(listing_entry_names, parsed_listing_entry_names)


class PrettifyListingsTestCase(unittest.TestCase):
    def test_prettify_no_elements(self):
        elements = {DEFAULT_TABLE: {}, RECURRENT_TABLE: {}}
        self.assertEqual(prettify(elements), "")

    def test_prettify(self):
        elements = {
            DEFAULT_TABLE: {
                1: {
                    "name": "food",
                    "value": -100.01,
                    "date": "2000-03-03",
                    "category": "groceries"
                },
                999: {
                    "name": "money",
                    "value": 299.99,
                    "date": "2000-03-03"
                }
            },
            RECURRENT_TABLE: {
                42: [{
                    "name": "gold",
                    "value": 4321,
                    "date": "2000-01-01",
                    "category": "bank"
                }]
            }
        }
        self.maxDiff = None
        elements_copy = elements.copy()
        self.assertEqual(
            prettify(
                elements_copy, default_category=CategoryEntry.DEFAULT_NAME),
            "                Earnings                  |                 Expenses                 \n"  # noqa
            "Name               Value    Date     ID   | Name               Value    Date     ID  \n"  # noqa
            "Unspecified          299.99               | Groceries            100.01              \n"  # noqa
            "  Money              299.99 00-03-03  999 |   Food               100.01 00-03-03    1\n"  # noqa
            "Bank                4321.00               | \n"  # noqa
            "  Gold              4321.00 00-01-01   42 | \n"  # noqa
            "=====================================================================================\n"  # noqa
            "Total               4620.99               | Total                100.01              \n"  # noqa
            "Difference          4520.98              ")
        # Assert that original data was not modified
        self.assertDictEqual(elements, elements_copy)

        self.assertEqual(
            prettify(
                elements_copy,
                default_category=CategoryEntry.DEFAULT_NAME,
                category_percentage=True),
            "                Earnings                  |                 Expenses                 \n"  # noqa
            "Name               Value           %      | Name               Value           %     \n"  # noqa
            "Unspecified          299.99      6.5      | Groceries            100.01    100.0     \n"  # noqa
            "Bank                4321.00     93.5      | \n"  # noqa
            "=====================================================================================\n"  # noqa
            "Total               4620.99               | Total                100.01              \n"  # noqa
            "Difference          4520.98              ")

    def test_prettify_stacked_layout(self):
        elements = {
            DEFAULT_TABLE: {
                2: {
                    "name": "shirt",
                    "value": -199,
                    "date": "2000-04-01",
                    "category": "clothes",
                },
                3: {
                    "name": "lunch",
                    "value": -20,
                    "date": "2000-04-01",
                    "category": "food",
                }
            },
            RECURRENT_TABLE: {}
        }
        self.maxDiff = None
        self.assertEqual(
            prettify(elements, stacked_layout=True), "\
                Earnings                 " + "\n\
Name               Value    Date     ID  " + "\n\
=========================================" + "\n\
Total                  0.00              " + """

""" + "\
                Expenses                 " + "\n\
Name               Value    Date     ID  " + "\n\
Food                  20.00              " + "\n\
  Lunch               20.00 00-04-01    3" + "\n\
Clothes              199.00              " + "\n\
  Shirt              199.00 00-04-01    2" + "\n\
=========================================" + "\n\
Total                219.00              " + "\n\
Difference          -219.00              ")


if __name__ == '__main__':
    unittest.main()
