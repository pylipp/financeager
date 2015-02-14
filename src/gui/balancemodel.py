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
from items import CategoryItem, SumItem, ExpenseItem, DateItem
from .. import settings 


class BalanceModel(QtGui.QStandardItemModel):
    """ 
    BalanceModel class for the Financeager application.
    Initialized with filled=False if filled with data from xml file. 
    IMPORTANT: parent is the corresponding TreeView.
    Required in the validateFloat() method. 
    """

    def __init__(self, parent=None, categories=None, filled=True):
        super(BalanceModel, self).__init__(parent)
        self.__valueItem = ExpenseItem('0')
        self.setHorizontalHeaderLabels(settings._HEADERLABELS_)
        if filled:
            for category in categories:
                self.appendRow(
                        [CategoryItem(category), SumItem(), DateItem()])
        # CONNECTIONS
        self.itemChanged.connect(self.validateFloat)

    def categoriesStringList(self):
        """
        Returns all the names of all the child categories in a string list. 
        Called from FinanceagerWindow.newEntry() to evaluate what model 
        (expenditures/receipts) to append the new entry to.

        :return     list[str]
        """
        return [unicode(self.item(r).text()) for r in range(self.rowCount())]

    def ctagtest2(self):
        pass 

    def child(self, row, col):
        """
        Helper function to make BalanceModel fit into the MonthTab.writeToXML routine.
        The returned child is a category.

        :param      row, col | int, int 
        :return     item 
        """
        index = self.index(row, col)
        return self.itemFromIndex(index)
    
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
        
    def validateFloat(self, item):
        #TODO implement analogous function for date input
        """
        Called whenever an item is changed. 
        Prompts the user with a warning if he gives a non-float input. 

        :param      item | item emitted from itemChanged() signal
        """
        if isinstance(item, ExpenseItem):
            try:
                newValue = float(item.text())
                oldValue = item.value()
                item.setValue(newValue)
                self.setSumItem(item, oldValue)
            except ValueError:
                QtGui.QMessageBox.warning(
                    self.parent().parentWidget(), 'Invalid Input!', 
                    'Please enter a floating point or integer number.')
                item.setText(str(item.value()))
                self.parent().setCurrentIndex(self.indexFromItem(item))

    def value(self):
        return self.__valueItem.value()

    def valueItem(self):
        return self.__valueItem 

    def xmlTag(self):
        return 'model'
