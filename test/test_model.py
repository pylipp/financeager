# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager import DEFAULT_TABLE
from financeager.model import Model, prettify
from financeager.entries import CategoryEntry, BaseEntry


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
            'test_str',
            'test_nonexisting_category_sum',
            ]
    suite.addTest(unittest.TestSuite(map(AddBaseEntryTestCase, tests)))
    tests = [
            'test_category_sum',
            'test_str'
            ]
    suite.addTest(unittest.TestSuite(map(AddNegativeBaseEntryTestCase, tests)))
    tests = [
        'test_sort_by_name',
        'test_sort_by_value',
    ]
    suite.addTest(unittest.TestSuite(map(SortCategoryEntriesTestCase, tests)))
    tests = [
            'test_default_category_in_list'
            ]
    suite.addTest(unittest.TestSuite(map(AddBaseEntryWithoutCategoryTestCase, tests)))
    tests = [
            'test_two_entries_in_list',
            'test_category_sum',
            'test_total_value'
            ]
    suite.addTest(unittest.TestSuite(map(AddTwoBaseEntriesTestCase, tests)))
    tests = [
            'test_category_sum_updated'
            ]
    suite.addTest(unittest.TestSuite(map(SetValueItemTextTestCase, tests)))
    tests = [
            'test_correct_item_is_found',
            'test_none_found',
            ]
    suite.addTest(unittest.TestSuite(map(FindItemByNameTestCase, tests)))
    tests = ['test_correct_item_is_found']
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
    tests = [
            'test_contains_an_entry',
            'test_category_item_names',
            'test_category_sums',
            'test_base_entries'
            ]
    suite.addTest(unittest.TestSuite(map(ModelFromElementsTestCase, tests)))
    tests = ['test_prettify']
    suite.addTest(unittest.TestSuite(map(PrettifyModelsTestCase, tests)))
    return suite


class AddCategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.category_name = "Groceries"
        self.model.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(),
                      self.model.category_entry_names)


class AddCategoryEntryTwiceTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.category_name = "Groceries"
        self.model.add_entry(CategoryEntry(name=self.category_name))
        self.model.add_entry(CategoryEntry(name=self.category_name))

    def test_category_item_in_list(self):
        self.assertIn(self.category_name.lower(),
                      self.model.category_entry_names)

    def test_single_item_in_list(self):
        self.assertEqual(1, len(list(self.model.category_entry_names)))


class AddBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.model.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_base_entry_in_list(self):
        base_entry_names = list(self.model.base_entry_fields("name"))
        self.assertIn(self.item_name.lower(), base_entry_names)

    def test_category_sum(self):
        self.assertAlmostEqual(
            self.item_value,
            self.model.category_sum(self.item_category),
            places=5)

    def test_nonexisting_category_sum(self):
        self.assertEqual(0.0, self.model.category_sum("black hole"))

    def test_str(self):
        self.assertEqual(
            str(self.model), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Model"),
                "Name               Value    Date  ID ",
                "Groceries             66.60" + 10 * " ",
                "  Aldi                66.60 11-08   0"
            ]))


class SortCategoryEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        for c, v in zip("ab", [20, 10]):
            self.model.add_entry(BaseEntry("foo", v, "01-01"), c)

    def test_sort_by_name(self):
        Model.CATEGORY_ENTRY_SORT_KEY = "name"
        self.assertEqual(
            str(self.model), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Model"),
                "Name               Value    Date  ID ",
                "A                     20.00" + 10 * " ",
                "  Foo                 20.00 01-01   0",
                "B                     10.00" + 10 * " ",
                "  Foo                 10.00 01-01   0",
            ]))

    def test_sort_by_value(self):
        Model.CATEGORY_ENTRY_SORT_KEY = "value"
        self.assertEqual(
            str(self.model), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Model"),
                "Name               Value    Date  ID ",
                "B                     10.00" + 10 * " ",
                "  Foo                 10.00 01-01   0",
                "A                     20.00" + 10 * " ",
                "  Foo                 20.00 01-01   0",
            ]))


class AddNegativeBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = -66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.model.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date),
            self.item_category)

    def test_category_sum(self):
        self.assertAlmostEqual(
            abs(self.item_value),
            self.model.category_sum(self.item_category),
            places=5)

    def test_str(self):
        self.assertEqual(
            str(self.model), '\n'.join([
                "{1:^{0}}".format(CategoryEntry.TOTAL_LENGTH, "Model"),
                "Name               Value    Date  ID ",
                "Groceries             66.60" + 10 * " ",
                "  Aldi                66.60 11-08   0"
            ]))


class AddBaseEntryWithoutCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.model.add_entry(
            BaseEntry(self.item_name, self.item_value, self.item_date))

    def test_default_category_in_list(self):
        names = list(self.model.category_entry_names)
        self.assertIn(CategoryEntry.DEFAULT_NAME, names)


class AddTwoBaseEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.date = "11-11"
        self.model.add_entry(
            BaseEntry("Aldi", self.item_a_value, self.date),
            self.item_category)
        self.model.add_entry(
            BaseEntry("Rewe", self.item_b_value, self.date),
            self.item_category)

    def test_two_entries_in_list(self):
        self.assertEqual(2, len(list(self.model.base_entry_fields("name"))))

    def test_category_sum(self):
        self.assertAlmostEqual(
            self.item_a_value + self.item_b_value,
            self.model.category_sum(self.item_category),
            places=5)

    def test_total_value(self):
        self.assertAlmostEqual(
            self.item_a_value + self.item_b_value,
            self.model.total_value(),
            places=5)


class SetValueItemTextTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.model.add_entry(
            BaseEntry("Aldi", self.item_a_value, "04-04"), self.item_category)

    def test_category_sum_updated(self):
        self.assertAlmostEqual(
            self.item_a_value,
            self.model.category_sum(self.item_category),
            places=5)


class FindItemByNameTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.base_entry = BaseEntry(self.item_name, self.item_value,
                                    self.item_date)
        self.model.add_entry(self.base_entry, self.item_category)

    def test_correct_item_is_found(self):
        self.assertEqual(self.base_entry.name,
                         self.model.find_base_entry(
                             name=self.item_name,
                             category=self.item_category).name)

    def test_none_found(self):
        self.assertIsNone(self.model.find_base_entry(name="fdsa"))


class FindItemWrongCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_name = "Aldi"
        self.item_value = 66.6
        self.item_date = "11-08"
        self.item_category = "Groceries"
        self.base_entry = BaseEntry(self.item_name, self.item_value,
                                    self.item_date)
        self.model.add_entry(self.base_entry, self.item_category)

    def test_correct_item_is_found(self):
        self.assertIsNone(self.model.find_base_entry(name=self.item_name))


class FindItemByNameAndDateTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_name = "Aldi"
        self.item_b_name = "Aldi"
        self.item_a_value = 66.6
        self.item_b_value = 1.00
        self.item_a_date = "11-08"
        self.item_b_date = "12-08"
        self.base_entry_a = BaseEntry(self.item_a_name, self.item_a_value,
                                      self.item_a_date)
        self.base_entry_b = BaseEntry(self.item_b_name, self.item_b_value,
                                      self.item_b_date)
        self.model.add_entry(self.base_entry_b)
        self.model.add_entry(self.base_entry_a)

    def test_correct_item_is_found(self):
        self.assertEqual(self.base_entry_a,
                         self.model.find_base_entry(
                             name=self.item_a_name, date=self.item_a_date))


class RemoveEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.item_a_value = 66.6
        self.item_b_value = 10.01
        self.item_category = "Groceries"
        self.item_date = "01-23"
        self.base_entry_a = BaseEntry("Aldi", self.item_a_value,
                                      self.item_date)
        self.base_entry_b = BaseEntry("Rewe", self.item_b_value,
                                      self.item_date)
        self.model.add_entry(self.base_entry_a, self.item_category)
        self.model.add_entry(self.base_entry_b, self.item_category)
        self.model.remove_entry(self.base_entry_a, category=self.item_category)

    def test_remaining_entry(self):
        self.assertEqual(
            list(self.model.base_entry_fields("name"))[0],
            self.base_entry_b.name)

    def test_category_sum(self):
        self.assertAlmostEqual(
            self.model.category_sum(self.item_category),
            self.item_b_value,
            places=5)


class ModelFromElementsTestCase(unittest.TestCase):
    def setUp(self):
        self.name = "Dinner for one"
        self.value = 99.9
        self.date = "12-31"
        self.model = Model.from_elements([
            dict(name=self.name, value=self.value, date=self.date, eid=0)])

    def test_contains_an_entry(self):
        self.assertIsNotNone(self.model.find_base_entry(date=self.date))

    def test_category_item_names(self):
        parsed_model_entry_names = list(self.model.category_entry_names)
        model_entry_names = [CategoryEntry.DEFAULT_NAME]
        self.assertListEqual(model_entry_names, parsed_model_entry_names)

    def test_category_sums(self):
        self.assertAlmostEqual(
            self.model.category_sum(CategoryEntry.DEFAULT_NAME),
            self.value,
            places=5)

    def test_base_entries(self):
        item = self.model.find_base_entry(
            name=self.name, category=CategoryEntry.DEFAULT_NAME)
        self.assertEqual(
            str(item), str(BaseEntry(self.name, self.value, self.date)))


class PrettifyModelsTestCase(unittest.TestCase):
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
        self.assertEqual(prettify(elements_copy),
"              Earnings                |               Expenses               \n"
"Name               Value    Date  ID  | Name               Value    Date  ID \n"
"Unspecified          299.99           | Groceries            100.01          \n"
"  Money              299.99 03-03 999 |   Food               100.01 03-03   1\n"
"Bank                4321.00           | \n"
"  Gold              4321.00 01-01  42 | \n"
"=============================================================================\n"
"Total               4620.99           | Total                100.01          "
                         )
        # Assert that original data was not modified
        self.assertDictEqual(elements, elements_copy)


if __name__ == '__main__':
    unittest.main()
