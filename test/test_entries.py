import unittest

from financeager.entries import BaseEntry, CategoryEntry
from financeager.entries import prettify as prettify_entry


class BaseEntryTestCase(unittest.TestCase):
    def test_attributes(self):
        entry = BaseEntry(**{
            "name": "groceries",
            "value": 123.45,
            "date": "2000-08-10"
        })

        self.assertEqual(entry.name, "groceries")
        self.assertAlmostEqual(entry.value, 123.45, places=5)
        self.assertEqual(entry.date, "00-08-10")
        self.assertEqual(entry.eid, 0)

    def test_leap_year_date(self):
        entry = BaseEntry(**{
            "name": "leap",
            "value": 1,
            "date": "2000-02-29",
        })
        self.assertEqual(entry.date, "00-02-29")


class NegativeBaseEntryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = BaseEntry(**{
            "name": "vw bully",
            "value": -6000,
            "date": "2000-01-01"
        })

    def test_name(self):
        self.assertEqual(self.entry.name, "vw bully")

    def test_value(self):
        self.assertEqual(self.entry.value, 6000)

    def test_str(self):
        expected = "Vw Bully".ljust(
            BaseEntry.NAME_LENGTH) + " " + " 6000.00 00-01-01"
        expected += "    0"
        self.assertEqual(str(self.entry), expected)

    def test_str_no_eid(self):
        expected = "Vw Bully".ljust(
            BaseEntry.NAME_LENGTH) + " " + " 6000.00 00-01-01"
        BaseEntry.SHOW_EID = False
        self.assertEqual(str(self.entry), expected)
        BaseEntry.SHOW_EID = True


class CategoryEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = CategoryEntry(name="gifts")

    def test_name(self):
        self.assertEqual(self.entry.name, "gifts")

    def test_value(self):
        self.assertEqual(self.entry.value, 0.0)

    def test_str(self):
        self.assertEqual(
            self.entry.string(), "Gifts".ljust(CategoryEntry.NAME_LENGTH) +
            " " + "0.00".rjust(BaseEntry.VALUE_LENGTH) + " " +
            BaseEntry.DATE_LENGTH * " " + (BaseEntry.EID_LENGTH + 1) * " "
            if BaseEntry.SHOW_EID else "")


class LongNegativeCategoryEntryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = CategoryEntry(
            name="This is quite a LOOONG Category",
            entries=[BaseEntry("entry", -100, "2000-08-13")])

    def test_name(self):
        self.assertEqual(self.entry.name, "this is quite a looong category")

    def test_value(self):
        self.assertEqual(self.entry.value, 100)

    def test_str(self):
        self.assertEqual(
            self.entry.string(),
            "This Is Quite A Lo " + "  100.00" + 9 * " " + 5 * " " + "\n" +
            "  Entry            " + "  100.00" + " 00-08-13 " + "   0")
        self.assertEqual(
            self.entry.string(total_listing_value=200),
            "This Is Quite A Lo " + "  100.00" + "     50.0" + 5 * " ")


class SortBaseEntriesTestCase(unittest.TestCase):
    def setUp(self):
        self.entry = CategoryEntry(
            name="letters",
            entries=[
                BaseEntry(l, v, "2000-0{}-11".format(9 - v), i)
                for l, v, i in zip("abc", (1, 5, 3), (7, 1, 3))
            ])

    def test_sort_by_name(self):
        # don't let trailing whitespaces of category name row being cleaned up
        self.assertEqual(
            self.entry.string(entry_sort="name"), "\
Letters                9.00              " + """
  A                    1.00 00-08-11    7
  B                    5.00 00-04-11    1
  C                    3.00 00-06-11    3""")

    def test_sort_by_value(self):
        self.assertEqual(
            self.entry.string(entry_sort="value"), "\
Letters                9.00              " + """
  A                    1.00 00-08-11    7
  C                    3.00 00-06-11    3
  B                    5.00 00-04-11    1""")

    def test_sort_by_date(self):
        self.assertEqual(
            self.entry.string(entry_sort="date"), "\
Letters                9.00              " + """
  B                    5.00 00-04-11    1
  C                    3.00 00-06-11    3
  A                    1.00 00-08-11    7""")

    def test_sort_by_eid(self):
        self.assertEqual(
            self.entry.string(entry_sort="eid"), "\
Letters                9.00              " + """
  B                    5.00 00-04-11    1
  C                    3.00 00-06-11    3
  A                    1.00 00-08-11    7""")


class PrettifyBaseEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.element = dict(
            name="soccer shoes",
            value=-123.45,
            date="04-01",
            category="sport equipment")

    def test_prettify(self):
        self.assertEqual(
            prettify_entry(
                self.element, default_category=CategoryEntry.DEFAULT_NAME), """\
Name    : Soccer Shoes
Value   : -123.45
Date    : 04-01
Category: Sport Equipment""")

    def test_prettify_default_category(self):
        element = self.element.copy()
        element["category"] = None
        self.assertEqual(
            prettify_entry(
                element, default_category=CategoryEntry.DEFAULT_NAME), """\
Name    : Soccer Shoes
Value   : -123.45
Date    : 04-01
Category: {}""".format(CategoryEntry.DEFAULT_NAME.capitalize()))


class PrettifyRecurrentEntryTestCase(unittest.TestCase):
    def setUp(self):
        self.element = dict(
            name="retirement money",
            value=567.0,
            category="income",
            frequency="monthly",
            start="01-01",
            end="12-31")

    def test_prettify(self):
        self.assertEqual(
            prettify_entry(
                self.element, default_category=CategoryEntry.DEFAULT_NAME), """\
Name     : Retirement Money
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")


if __name__ == '__main__':
    unittest.main()
