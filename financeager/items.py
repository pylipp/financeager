#!/usr/bin/python

""" Defines custom Items, the fundamental elements for building models."""

# authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4.QtGui import QStandardItem
from PyQt4.QtCore import (QString, QDate)
from abc import ABCMeta

class DataItem(QStandardItem):
    """Abstract base class for all items that hold data.

    At initialization, the item data is set. By default, an instance of
    `DataItem` is editable. Finally, the item text is set by formatting the
    corresponding data. The formatting via `text()` is defined in the
    subclasses. The `entry` member refers to the parent entry if it exists.
    """
    # __metaclass__ = ABCMeta

    def __init__(self, data, entry=None):
        super(DataItem, self).__init__()
        self.setData(data)
        self.setEditable(True)
        self.setText(self.text())
        self._entry = entry

    @property
    def entry(self):
        return self._entry

class EmptyItem(DataItem):
    """Represents an empty item in the third column of a category row. """

    def __init__(self, entry=None):
        super(EmptyItem, self).__init__(None, entry)
        self.setEditable(False)

class NameItem(DataItem):
    """Item representing the name of an entry.

    Holds a lowercase `QString` as data. When its text is requested, an
    uppercase representation is returned.

    :param data: Python string
    """

    def __init__(self, data, entry=None):
        #TODO handle empty name
        super(NameItem, self).__init__(data.lower(), entry)

    def text(self):
        # workaround because QString has no capitalize method
        text_ = unicode(self.data().toString())
        capitalized = u' '.join([t.capitalize() for t in text_.split()])
        return QString(capitalized)

    def setText(self, text_):
        super(NameItem, self).setText(text_)
        self.setData(text_.toLower())

class CategoryItem(NameItem):
    """Item representing the name of a category.

    Cannot be edited. Text is printed in bold letters.
    """
    DEFAULT_NAME = "unspecified"

    def __init__(self, data, entry=None):
        super(CategoryItem, self).__init__(data, entry)
        self.setEditable(False)
        font = self.font()
        font.setBold(True)
        self.setFont(font)

class ValueItem(DataItem):
    """Item representing the value of an entry.

    Holds a `QFloat` number as data. When its text is requested, the return format
    has two decimal points. If input with sub-percent precision is given, it is
    rounded.

    :param data: Python integer or float number
    """
    def __init__(self, data, entry=None):
        super(ValueItem, self).__init__(data, entry)
        # TODO add sign attribute

    def text(self):
        value, ok = self.data().toFloat()
        # should not fail...
        # TODO negative numbers should be displayed without minus sign
        if ok:
            return QString.number(value, 'f', 2)

    def setText(self, text_):
        value, ok = text_.toFloat()
        if ok:
            super(ValueItem, self).setText(text_)
            self.setData(value)

    @property
    def value(self):
        val, ok = self.data().toFloat()
        if ok:
            return val
        return 0.0

class DateItem(DataItem):
    """Item representing the date of an entry.

    Holds a `QDate` as data. If an invalid data is given at initialization,
    today's date is used instead.
    """
    FORMAT = "yyyy-MM-dd"
    def __init__(self, data="", entry=None):
        date = QDate.fromString(data, DateItem.FORMAT)
        if not date.isValid():
            date = QDate.currentDate()
        super(DateItem, self).__init__(date, entry)

    def text(self):
        # assume the conversion to date does not fail
        return self.data().toDate().toString(DateItem.FORMAT)

    def setText(self, text_):
        date  = QDate.fromString(text_, DateItem.FORMAT)
        if date.isValid():
            super(DateItem, self).setText(text_)
            self.setData(date)

# deprecated, replaced by ValueItem
class ExpenseItem(QStandardItem):
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


# deprecated
class ResultItem(QStandardItem):
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


class SumItem(ValueItem):
    """Item representing the sum of entry values of a category.

    Is updated when new entries are added. Not editable. The text will be
    represented in bold.
    """

    def __init__(self, data=0.0, entry=None):
        super(SumItem, self).__init__(data, entry)
        self.setEditable(False)
        font = self.font()
        font.setBold(True)
        self.setFont(font)
