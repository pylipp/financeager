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


from PyQt4 import QtGui 
from PyQt4.QtCore import QDate 
from . import _FONT_ 

class CategoryItem(QtGui.QStandardItem):
    """ Represents a category item. """

    def __init__(self, text=""):
        super(CategoryItem, self).__init__(text)
        self.setEditable(False)
        self.setFont(_FONT_)

    def xmlTag(self):
        return 'category'
     

class DateItem(QtGui.QStandardItem):
    """ Represents a date item. """
    def __init__(self, text=""):
        super(DateItem, self).__init__(text)
        self.setEditable(False)


class EntryItem(QtGui.QStandardItem):
    """ Represents an entry item. """

    def __init__(self, text=""):
        super(EntryItem, self).__init__(text)

    def sibling(self, row, col):
        # TODO this is deprecated 
        """
        Workaround to get the sibling of item self at row and col. 

        :param      row, col | int 
        :return     QStandardItem 
        """
        return self.model().itemFromIndex( 
                self.model().sibling(row, col, self.index()))

    def xmlTag(self):
        return 'entry'


class ExpenseItem(QtGui.QStandardItem):
    """ Represents an expense item. Accepts only float as text. """

    def __init__(self, text=""):
        super(ExpenseItem, self).__init__(text)
        if not len(text):
            text = '0'
        self.__value = float(text)

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
