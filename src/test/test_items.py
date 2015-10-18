import unittest
from hypothesis import given, Settings
from hypothesis.strategies import text
from hypothesis.extra.datetime import dates

from datetime import date

from ..gui.items import EntryItem, DateItem
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

if __name__ == '__main__':
    unittest.main()
