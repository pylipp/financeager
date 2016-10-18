#!/usr/bin/python

""" Defines custom Items for the MonthTreeView. """

# authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4 import QtGui, QtCore
from . import _FONT_ 

class CategoryItem(QtGui.QStandardItem):
    """ Represents a category item. """

    def __init__(self, text=""):
        super(CategoryItem, self).__init__(text)
        self.setEditable(False)
        self.setFont(_FONT_)

    def appendRow(self, itemList, updateSumItem=True):
        """
        Re-implemented method.
        Set updateSumItem=False if the row is read from xml (and the SumItem,
        too).

        :param      updateSumItem | bool 
        """
        super(CategoryItem, self).appendRow(itemList)
        if updateSumItem:
            # ExpenseItem is the second entry of the row
            self.model().setSumItem(itemList[1])

    def xmlTag(self):
        return 'category'
     
#TODO classes DateItem, EntryItem and ExpenseItem could be nicely derived from
#     base class ValueItem or something 
class DateItem(QtGui.QStandardItem):
    """ 
    Represents a date item holding a QVariant with data. 
    Can be constructed from a string ('21.'), an int (21) or a QDate object. 
    """
    def __init__(self, day, month=None, year=None):
        text = ""
        data = None
        if isinstance(day, int):
            text = str(day) + '.'
            data = QtCore.QDate(year, month, day)
        elif isinstance(day, QtCore.QDate):
            text = str(day.day()) + '.'
            data = day
        elif isinstance(day, str) or isinstance(day, unicode):
            text = day
            data = QtCore.QDate(year, month, int(day[:-1]))
        super(DateItem, self).__init__(text)
        self.setData(data)
        self.__value = text

    def value(self):
        return self.__value


class EmptyItem(QtGui.QStandardItem):
    """ Represents an empty item in the third column of a category row. """
    def __init__(self):
        super(EmptyItem, self).__init__()
        self.setEditable(False)


class EntryItem(QtGui.QStandardItem):
    """ Represents an entry item. """

    def __init__(self, text=""):
        super(EntryItem, self).__init__(text)
        self.__value = text

    def setText(self, text):
        self.__value = text 
        super(EntryItem, self).setText(text)

    def value(self):
        return self.__value 

    def xmlTag(self):
        return 'entry'


class ExpenseItem(QtGui.QStandardItem):
    """ Represents an expense item. Accepts only float as text. """

    def __init__(self, data=None):
        """ 
        Can be initialized in three ways: With data=None, an ExpenseItem with
        value zero is created. Otherwise, the value is deduced from an input
        string or number.

        :param      data | str, int, float or None 
        """
        text = ""
        value = 0.0
        if data is None:
            text = "0.0"
        elif isinstance(data, int):
            text = str(data)
            value = float(data)
        elif isinstance(data, float):
            text = str(data)
            value = data
        elif isinstance(data, str) or isinstance(data, unicode):
            text = data 
            value = float(data)
        super(ExpenseItem, self).__init__(text)
        self.__value = value

    def value(self):
        return self.__value 

    def setValue(self, value):
        self.__value = value 
        self.setText(str(value))
        

class ResultItem(QtGui.QStandardItem):
    """ 
    Represents an item displayed in the SearchDialog.
    The text of name, value and category entries is the string representation
    of their data. The text of the date entry is formatted. 
    
    :param      data | str, float, QDate 
    """
    def __init__(self, data=None):
        super(ResultItem, self).__init__()
        self.setEditable(False)
        self.setData(data)
        # self.data() required here (returns a QVariant)
        if self.data().toDate().isValid():
            data = data.toDate().toString('dd\'.\'MM\'.\'')
        self.setText(unicode(data))


class SumItem(QtGui.QStandardItem):
    """ Represents a sum item. Set by the system. """

    def __init__(self, text=""):
        super(SumItem, self).__init__(text)
        if not len(text):
            text = '0'
        self.__value = float(text)
        self.setFont(_FONT_)
        self.setEditable(False)

    def increment(self, newValue, oldValue):
        self.__value = self.__value - oldValue + newValue 
        self.setText(str(self.__value))
        self.setEditable(False)

    def value(self):
        return self.__value 
