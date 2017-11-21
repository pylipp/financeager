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
    Handles undoing and redoing of item related actions in the MainWindow, i.e.
    modifying entries or removing rows.
    """
    def __init__(self, mainWindow=None):
        """
        Requires direct reference to MainWindow. 
        Holds two lists. items contains ItemRows that have been modified and
        are waiting to be undone. undoneItems contains ItemRows that have been
        undone and are waiting to be redone. 
        
        :param      mainWindow | FinanceagerWindow 
        :attrib     __mainWindow | FinanceagerWindow 
                    __items | list[ItemRow]
                    __undoneItems | list[ItemRow]
        """
        self.__mainWindow = mainWindow 
        self.__items = [] 
        self.__undoneItems = []

    def addAction(self, itemRow):
        """
        Append a new ItemRow after an action (modifying, removing) has been
        performed in the mainwindow.

        :param      itemRow | ItemRow 
        """
        self.__items.append(itemRow)

    def undoAction(self):
        """
        Undo the action performed last. 
        """
        self.doAction(self.__items, self.__undoneItems)

    def doAction(self, popList, appendList):
        """
        Resets the current state to the state given in popList and appends the
        current state to the appendList. 
        Enables the buttons in MainWindow accordingly.
        
        :param      popList | list[ItemRow]
                    appendList | list[ItemRow] 
        """
        itemRow = popList.pop()
        category = itemRow.category 
        if category is None:
            return
        row = itemRow.row 
        if itemRow.removed:
            name, expense, date = itemRow.content
            expenseItem = ExpenseItem(expense)
            newRow = [EntryItem(name), expenseItem, DateItem(date)]
            itemRow.category.insertRow(row, newRow)
            itemRow.category.model().setSumItem(expenseItem)
        else:
            content = itemRow.content[0]
            child = category.child(row, itemRow.col)
            replaced = str(child.value())
            if row == 1:
                child.setValue(float(content))
            else:
                child.setText(content)
            replacedRow = ItemRow(category, (replaced,), row, itemRow.col)
            appendList.append(replacedRow)
        self.__mainWindow.action_Undo.setEnabled(len(self.__items))
        self.__mainWindow.action_Redo.setEnabled(len(self.__undoneItems))

    def redoAction(self):
        #FIXME does not do stuff
        pass
        self.doAction(self.__undoneItems, self.__items)


class ItemRow(object):
    """
    Simple class containing all information required to restore a row or an
    entry. 
    """
    def __init__(self, category=None, content=None, row=None, col=None):
        """
        If col is None, the 'removed' flag is set to True, indicating that the
        current instance represents a deleted row.

        :param      category | QStandardItem 
                    content | tuple[str] with entry name, value, date 
                    row | int 
                    col | int 
        """
        self.category = category
        self.row = row 
        self.col = col 
        self.content = content
        self.removed = col is None
