#!/usr/bin/python

""" Defines the StatisticsWindow Popup for the Financeager application. """

# define authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4 import QtGui, QtCore 
from items import ExpenseItem 
from . import loadUi, _MONTHS_ 

class StatisticsWindow(QtGui.QDialog):
    """
    StatisticsWindow class for the Financeager application.
    This window can be opened by either clicking the corresponding button in
    the toolbar or typing the shortcut CTRL-t. 
    It displays a table with receipts, expenditures and their difference for
    all twelve months. 
    The widget basically is a QTreeView that is populated with a
    QStandardItemModel created from the FinanceagerWindow's items.
    
    :attribute      self.__totals | list 
                    Keeps track of total expenditures and receipts, resp.
                    Updated via updateTotalItems() upon item change. 
    """

    def __init__(self, parent=None):
        """
        Loads the ui layout file. 
        Populates the model and does some layout adjustments. 
        
        :param      parent | FinanceagerWindow 
        """
        super(StatisticsWindow, self).__init__(parent)
        loadUi(__file__, self)

        self.__model = QtGui.QStandardItemModel(self.tableView)
        self.__model.setHorizontalHeaderLabels(
                ['Expenditures', 'Receipts', 'Differences'])
        self.__model.setVerticalHeaderLabels(_MONTHS_ + ['TOTAL'])
        monthsTabWidget = self.parentWidget().monthsTabWidget
        for r in range(12):
            self.__model.setItem(r, 0, monthsTabWidget.widget(r).expendituresModel().valueItem())
            self.__model.setItem(r, 1, monthsTabWidget.widget(r).receiptsModel().valueItem())
            self.__model.setItem(r, 2, ExpenseItem())
        for c in range(3):
            self.__model.setItem(12, c, ExpenseItem())
        self.__totals = [0, 0]
        self.updateTotalItems(QtGui.QStandardItem())
        self.tableView.setModel(self.__model)

        self.tableView.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tableView.adjustSize()
        self.setWindowTitle('Statistics of ' + str(parent.year()))
        self.setFixedSize(self.size())
        # CONNECTIONS
        self.__model.itemChanged.connect(self.updateTotalItems)

    def closeEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        self.parentWidget().action_Statistics.setChecked(False)
        event.accept()

    def keyPressEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        if event.key() == QtCore.Qt.Key_Escape:
            self.parentWidget().action_Statistics.setChecked(False)
        super(StatisticsWindow, self).keyPressEvent(event)

    def updateTotalItems(self, item):
        """
        Whenever an item in the table is changed, one of the 'total' items 
        needs to be updated, i.e. the sum of all month values is calculated.
        Also, the corresponding value in third column (difference) is updated.
        This function is ignored if an item in the third column is changed
        (this will happen because Item.setValue() emits itemChanged() signal).
        At the initialization of StatisticsWindow, this function is called with
        a generic QStandardItem (default attributes row, column = -1). This is
        exploited in order to update all cells at initialization but only
        update the row/column of the changed item at any later point in time.

        :param      item | Item emitted from itemChanged() signal
        """
        if item.column() == 2:
            return 
        elif item.column() == -1:
            cols = [0, 1]
        else:
            cols = [int(item.column())]
        for c in cols:
            self.__totals[c] = 0
        for r in range(12):
            for c in cols:
                self.__totals[c] += self.__model.item(r, c).value()
            if item.row() == -1 or item.row() == r:
                # calculate difference in resp. row and update 3rd column 
                self.__model.item(r, 2).setValue(
                        self.__model.item(r, 1).value() - self.__model.item(r, 0).value())
        for c in cols:
            # update items in bottom row
            self.__model.item(12, c).setValue(self.__totals[c])
        difference = self.__totals[1] - self.__totals[0]
        # update item in bottom right corner (= total balance)
        self.__model.item(12, 2).setValue(difference)
