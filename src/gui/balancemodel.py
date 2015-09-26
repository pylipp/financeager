#!/usr/bin/python

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
from items import (CategoryItem, SumItem, ExpenseItem, DateItem, EntryItem,
    EmptyItem)
from . import _HEADERLABELS_, _DATEVALIDATOR_
from undocontainer import ItemRow


class BalanceModel(QtGui.QStandardItemModel):
    """ 
    BalanceModel class for the Financeager application.
    """

    def __init__(self, parent=None, categories=None, filled=True):
        """
        Initialized with filled=False if filled with data from xml file. 
        filled=True will fill the models with default categories.

        :param      parent | FinanceagerWindow 
                    categories | list[str]
                    filled | bool 
        """
        super(BalanceModel, self).__init__(parent)
        self.__mainWindow = parent
        self.__valueItem = ExpenseItem()
        self.setHorizontalHeaderLabels(_HEADERLABELS_)
        if filled:
            for category in categories:
                self.appendRow(
                        [CategoryItem(category), SumItem(), EmptyItem()])
        # CONNECTIONS
        self.itemChanged.connect(self.validate)

    def categoriesStringList(self):
        """
        Returns all the names of all the child categories in a string list. 
        Called from FinanceagerWindow.newEntry() to evaluate what model 
        (expenditures/receipts) to append the new entry to.

        :return     list[str]
        """
        return [unicode(self.item(r).text()) for r in range(self.rowCount())]

    def child(self, row, col):
        """
        Helper function to make BalanceModel fit into the MonthTab.writeToXML routine.
        The returned child is a category.

        :param      row, col | int, int 
        :return     item 
        """
        index = self.index(row, col)
        return self.itemFromIndex(index)
    
    def clear(self):
        """ 
        Reimplementation. Also sets the header labels. 
        """
        super(BalanceModel, self).clear()
        self.setHorizontalHeaderLabels(_HEADERLABELS_)

    def setSumItem(self, item, oldValue=0):
        """
        Fetches the sumItem corresponding to item and updates it.
        Also updates the model's value item. 
        
        :param      item | ExpenseItem 
                    oldValue | float 
        """
        sumItem = item.model().child(item.parent().row(), 1)
        sumItem.increment(item.value(), oldValue)
        self.updateValueItem()

    def setValueItem(self, value):
        """ Called by FinanceagerWindow.parseXMLtoModel. """
        self.__valueItem = ExpenseItem(value)

    def updateValueItem(self):
        """ Holds the sum of the model values (sum of category values). """
        value = 0.0
        for r in range(self.rowCount()):
            value += self.child(r, 1).value()
        self.__valueItem.setValue(value)
        
    def validate(self, item):
        """
        Called whenever an item is changed. 
        Calls subfunction according to the type of item.
        Also updates the UndoContainer with a new ItemRow.

        :param      item | item emitted from itemChanged() signal 
        """
        #FIXME should be moved into Item classes
        #return a bool and an error code if False
        valid = True
        if isinstance(item, ExpenseItem):
            valid = self.validateFloat(item)
        elif isinstance(item, DateItem):
            valid = self.validateDate(item)
        elif isinstance(item, EntryItem):
            valid = self.validateEntry(item)
        replaced = unicode(item.value())
        if valid:
            replacedRow = ItemRow(item.parent(), (replaced,), item.row(),
                    item.column())
            self.__mainWindow.undoContainer.addAction(replacedRow)
            self.__mainWindow.action_Undo.setEnabled(True)
            self.__mainWindow.updateSearchDialog(item)

    def validateDate(self, item):
        """
        Does a two-stage check if user gives a new date as input. 
        First, QRegExpValidator checks if the input matches the regular
        expression '\d{1,2}\.', i.e. a one- or two-digit number followed by a
        dot. If this is accepted, a QDate with the new day is created. If this
        is valid (depends on the month, internally handled by QDate), the new
        date is assigned to the item.
        If any of those validations fails, the user is prompted with a warning
        and the date is reset.

        :param      item | DateItem 
        :return     valid | bool
        """
        state = _DATEVALIDATOR_.validate(item.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            newDay = unicode(item.text()) #str 'dd.
            year, month, _ = item.data().toDate().getDate()
            date = QDate(year, month, int(newDay[:-1])) #skip trailing . of day
            if date.isValid():
                item.setData(date)
                return True
        QtGui.QMessageBox.warning(None, 'Invalid input!', 
                'Please enter a valid day of the format \'dd.\'')
        item.setText(str(item.data().toDate().day()) + '.')

    def validateFloat(self, item):
        """
        Prompts the user with a warning if he gives a non-float input. 

        :param      item | ValueItem
        :return     valid | bool
        """
        try:
            newValue = float(item.text())
            oldValue = item.value()
            item.setValue(newValue)
            self.setSumItem(item, oldValue)
            return True
        except ValueError:
            QtGui.QMessageBox.warning(None, 'Invalid Input!', 
                'Please enter a floating point or integer number.')
            item.setText(str(item.value()))

    def validateEntry(self, item):
        """
        Prompts the user with a warning if he gives a zero-length input as
        entry name.

        :param      item | EntryItem 
        :return     valid | bool 
        """
        if item.text().length():
            return True 
        else:
            QtGui.QMessageBox.warning(None, 'Invalid Input!', 
                'Please enter a string of non-zero length.')
            item.setText(str(item.value()))

    def value(self):
        return self.__valueItem.value()

    def valueItem(self):
        return self.__valueItem 

    def xmlTag(self):
        return 'model'
