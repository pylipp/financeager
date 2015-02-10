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


from PyQt4.QtGui import QDialog, QDialogButtonBox 
from PyQt4.QtCore import pyqtSignal
from . import loadUi, _CURRENTMONTH_ 
from categoriestab import CategoriesTab 
from filesavingtab import FileSavingTab 
from items import CategoryItem, SumItem 


class SettingsDialog(QDialog):
    """ 
    Dialog class to administer the settings of Financeager.
    Parent is the FinanceagerWindow. 
    Contains several tabs (Categories, File saving)
    """
    autoSaveSet = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        loadUi(__file__, self)
        # stores changes when ApplyButton is clicked
        self.__changes = set()

        self.buttonBox.button(QDialogButtonBox.Apply).setDefault(True)
        self.tabWidget.clear()
        self.categoriesTab = CategoriesTab(parent)
        self.fileSavingTab = FileSavingTab(parent)
        self.tabWidget.addTab(self.categoriesTab, 'Categories')
        self.tabWidget.addTab(self.fileSavingTab, 'File saving')
        # CONNECTIONS
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.updateChangesToApply)

    def addCategory(self, parameters):
        """ 
        Creates a new row consisting of a CategoryItem and a SumItem and 
        appends it to the according model (given by typ) of the according 
        monthTabs (given by option).

        :param      parameters | tuple of   name | str 
                                            typ | int (0 or 1)
                                            option | int (0, 1 or 2)
        """
        name, typ, option = parameters 
        tabWidget = self.parentWidget().monthsTabWidget
        months = self.monthsRange(option)
        for m in months:
            monthTab = tabWidget.widget(m)
            row = [CategoryItem(name), SumItem()]
            if typ == 0:
                monthTab.expendituresModel().appendRow(row)
            elif typ == 1:
                monthTab.receiptsModel().appendRow(row)

    def applyChanges(self):
        """
        Called from FinanceagerWindow when OK pressed and dialog closed. 
        Then the changes in the changes set are actually applied. 
        """
        for change in self.__changes:
            getattr(self, change[0])(change[1])

    def monthsRange(self, option):
        """
        Returns a list of month indices according to option. 
        
        :param      option | int (0, 1 or 2)
        :return     list 
        """
        months = None 
        if option == 0:
            months = range(12)
        elif option == 1:
            months = range(_CURRENTMONTH_, 12)
        elif option == 2:
            months = range(_CURRENTMONTH_, _CURRENTMONTH_ + 1)
        return months 

    def removeCategory(self, parameters):
        """
        Searches the models of the according MonthTabs (given by option) 
        for the to-be-removed item (given by name). 
        Deletes the item's row if the item exists in the current MonthTab.

        :param      parameters | tuple of   name | str 
                                            option | int (0, 1 or 2)
        """
        name, option = parameters
        tabWidget = self.parentWidget().monthsTabWidget
        months = self.monthsRange(option)
        for m in months:
            monthTab = tabWidget.widget(m)
            # pray that no items with the same name exist!!
            item = monthTab.expendituresModel().findItems(name)
            if item:
                monthTab.expendituresModel().removeRow(item[0].row())
            else:
                item = monthTab.receiptsModel().findItems(name)
                if item:
                    monthTab.receiptsModel().removeRow(item[0].row())

    def setAutoSave(self, value):
        #self.parent().autoSave = value 
        self.autoSaveSet.emit(value)

    def setFileName(self, fileName):
        self.parent().fileName = fileName 
    def updateChangesToApply(self):
        self.categoriesTab.updateChangesToApply(self.__changes)
        self.fileSavingTab.updateChangesToApply(self.__changes)
