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
from .. import settings 
from . import loadUi 

class StatisticsWindow(QtGui.QDialog):
    """StatisticsWindow class for the Financeager application. """
    #TODO implement third column that shows net income 

    def __init__(self, parent=None):
        super(StatisticsWindow, self).__init__(parent)
        loadUi(__file__, self)
        self.setFixedSize(self.size())
        self.setWindowTitle('Statistics of ' + str(parent.year()))
        # Set up the model 
        self.__model = QtGui.QStandardItemModel(self.tableView)
        self.__model.setHorizontalHeaderLabels(['Expenditures', 'Receipts'])
        self.__model.setVerticalHeaderLabels(settings._MONTHS_ + ['TOTAL'])
        monthsTabWidget = self.parentWidget().monthsTabWidget
        for r in range(12):
            self.__model.setItem(r,0, monthsTabWidget.widget(r).expendituresModel().valueItem())
            self.__model.setItem(r,1, monthsTabWidget.widget(r).receiptsModel().valueItem())
        self.__model.setItem(12, 0, ExpenseItem('0'))
        self.__model.setItem(12, 1, ExpenseItem('0'))
        self.__totals = [0, 0]
        self.updateTotalItems(self.__model.item(0, 0))
        self.updateTotalItems(self.__model.item(0, 1))
        self.tableView.setModel(self.__model)
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

        :param      item | Item emitted from itemChanged() signal
        """
        total = 0.0
        c = int(item.column())
        for r in range(12):
            total += self.__model.item(r, c).value()
        self.__model.item(12, c).setValue(total)
        self.__totals[c] = total 
        difference = self.__totals[1] - self.__totals[0]
        self.label.setText('TOTAL BALANCE \n%.2f - %.2f = %.2f' % 
                (self.__totals[1], self.__totals[0], difference))
