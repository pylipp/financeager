import unittest
from hypothesis import given, Settings, assume
from hypothesis.strategies import text, integers, floats, one_of, none
from hypothesis.extra.datetime import dates

from datetime import date
from math import isnan

from ..gui.items import EntryItem, DateItem, ExpenseItem
from PyQt4.QtCore import QString, QDate


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_value',
            'test_set_value'
            ]
    suite.addTest(unittest.TestSuite(map(EntryItemValueTestCase, tests)))
    tests = [
            'test_date'
            ]
    suite.addTest(unittest.TestSuite(map(DateItemDataTestCase, tests)))
    tests = [
            'test_value',
            'test_set_value'
            ]
    suite.addTest(unittest.TestSuite(map(ExpenseItemValueTestCase, tests)))
    return suite


class EntryItemTestCase(unittest.TestCase):

    @given(text())
    def setUp(self, s):
        self.item = EntryItem(s)
        self.s = s


class EntryItemValueTestCase(EntryItemTestCase):

    def test_value(self):
        self.assertEqual(self.item.value(), self.s)
        self.assertEqual(self.item.text(), QString(self.s))
    
    @given(text())
    def test_set_value(self, s):
        self.item.setText(s)
        self.assertEqual(self.item.value(), s)
        self.assertEqual(self.item.text(), QString(s))
    
        
class DateItemTestCase(unittest.TestCase):
        
    @given(dates(), settings=Settings(max_examples=500))
    def setUp(self, d):
        self.items = [
                DateItem(d.day, d.month, d.year),
                DateItem(str(d.day)+'.', d.month, d.year),
                DateItem(unicode(str(d.day)+'.'), d.month, d.year),
                DateItem(QDate(d.year, d.month, d.day))]
        self.date = d


class DateItemDataTestCase(DateItemTestCase):

    def _dataAsPyDate(self, item):
        """ Method to convert item's data (QDate) to datetime.date """
        d = item.data().toDate()
        if d.isValid():
            return d.toPyDate()
        else:
            return date(1, 1, 1)

    def test_date(self):
        for item in self.items:
            self.assertEqual(self._dataAsPyDate(item), self.date)


class ExpenseItemTestCase(unittest.TestCase):

    @given(one_of(integers(min_value=0), floats(min_value=0.0), none()))
    def setUp(self, val):
        if val is not None:
            assume(not isnan(val))
        self.items = dict()
        self.items[ExpenseItem()] = None 
        self.items[ExpenseItem(val)] = val
        if val is not None:
            self.items[ExpenseItem(str(val))] = val
            self.items[ExpenseItem(unicode(val))] = val


class ExpenseItemValueTestCase(ExpenseItemTestCase):

    def test_value(self):
        for item, value in self.items.iteritems():
            if value is None:
                self.assertAlmostEqual(item.value(), 0.0, places=3)
                self.assertEqual(item.text(), QString(str(0.0)))
            else:
                self.assertAlmostEqual(item.value(), value, places=3)
                self.assertEqual(item.text(), QString(str(value)))

    @given(one_of(integers(min_value=0), floats(min_value=0.0)))
    def test_set_value(self, v):
        for item in self.items.iterkeys():
            item.setValue(v)
            self.assertAlmostEqual(item.value(), v)
            self.assertEqual(item.text(), QString(str(v)))


if __name__ == '__main__':
    unittest.main()
