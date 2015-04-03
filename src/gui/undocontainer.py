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

from items import EntryItem, ExpenseItem, DateItem

class UndoContainer(object):
    """ 
    """

    def __init__(self, mainWindow=None):
        self.__mainWindow = mainWindow 
        self.__items = [] 
        self.__undoneItems = []

    def addAction(self, itemRow):
        self.__items.append(itemRow)

    def undoAction(self):
        itemRow = self.__items.pop()
        category = itemRow.category 
        row = itemRow.row 
        if itemRow.removed:
            from PyQt4 import QtCore; import pdb; QtCore.pyqtRemoveInputHook(); pdb.set_trace()
            name, expense, date = itemRow.content
            expenseItem = ExpenseItem(expense)
            newRow = [EntryItem(name), expenseItem, DateItem(date)]
            itemRow.category.insertRow(row, newRow)
            itemRow.category.model().setSumItem(expenseItem)
        else:
            content = itemRow.content[0]
            child = category.child(row, itemRow.col)
            if row == 1:
                replaced = str(child.value())
                child.setValue(float(content))
            else:
                replaced = unicode(child.text())
                child.setText(content)
            replacedRow = ItemRow(category, (replaced,), row, itemRow.col)
            self.__undoneItems.append(replacedRow)
        if not self.__items:
            self.__mainWindow.action_Undo.setEnabled(False)

    def redoAction(self):
        pass


class ItemRow(object):
    """
    """
    def __init__(self, category=None, content=None, row=None, col=None):
        self.category = category
        self.row = row 
        self.col = col 
        self.content = content
        self.removed = col is None
