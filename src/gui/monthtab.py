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


from PyQt4.QtGui import QStandardItem, QStandardItemModel, QWidget, QHeaderView
from PyQt4.QtCore import QDate 
from . import loadUi, _MONTHS_, _HEADERLABELS_, _EXPCATEGORIES_, _RECCATEGORIES_
from items import (CategoryItem, SumItem, EntryItem, ExpenseItem, DateItem,
    EmptyItem)
from balancemodel import BalanceModel 


class MonthTab(QWidget):
    """ MonthTab class for the Financeager application. """

    def __init__(self, parent=None, month=None, filled=True):
        """
        Loads the ui file and sets several attributes.
        Pass filled=True if you want to load the widget with default
        categories.

        :param      parent | FinanceagerWindow 
                    month | str 
                    filled | bool 
        :attrib     __mainWindow | FinanceagerWindow 
                    __month | str 
                    __monthIndex | int 
                    __expendituresModel | BalanceModel 
                    __receiptsModel | BalanceModel 
                    __categoriesModel | QStandardItemModel 
        """
        super(MonthTab, self).__init__(parent)
        loadUi(__file__, self)
        self.__mainWindow = parent
        self.__month = month 
        self.__monthIndex = _MONTHS_.index(month)
        self.__expendituresModel = None 
        self.__receiptsModel = None 
        self.__categoriesModel = QStandardItemModel()
        self.setModels(filled)
        self.setViews()

    def categoriesModel(self):
        """
        Fills the categoriesModel with the month's categories 
        (both expenditures and receipts). 
        This model can be set to the ComboBoxes in NewEntryDialog and the 
        CategoriesTab of the SettingsDialog. 

        :return     QStandardItemModel 
        """
        self.__categoriesModel.clear()
        for r in range(self.__expendituresModel.rowCount()):
            item = QStandardItem(unicode(self.__expendituresModel.item(r).text()))
            self.__categoriesModel.appendRow(item)
        for r in range(self.__receiptsModel.rowCount()):
            item = QStandardItem(unicode(self.__receiptsModel.item(r).text()))
            self.__categoriesModel.appendRow(item)
        return self.__categoriesModel 

    def categoriesStringList(self):
        """
        Returns all the names of all the child categories in a string list. 
        Called from CategoriesTab in SettingsDialog to fill the 
        removeCategoryCombo.

        :return     list[str]
        """
        categoriesModel = self.categoriesModel()
        return [unicode(categoriesModel.item(r).text()) 
                for r in range(categoriesModel.rowCount())]

    def entriesStringList(self):
        """
        Returns names of all entries of the current month in a string list. To
        avoid duplication, a set is created first and then converted to a list.
        This is used to feed the QCompleter of NewEntryDialog.

        :return     list[str]
        """
        entries = set()
        for r in range(self.__expendituresModel.rowCount()):
            category = self.__expendituresModel.item(r, 0)
            for e in range(category.rowCount()):
                entries.add(unicode(category.child(e, 0).text()))
        for r in range(self.__receiptsModel.rowCount()):
            category = self.__receiptsModel.item(r, 0)
            for e in range(category.rowCount()):
                entries.add(unicode(category.child(e, 0).text()))
        return list(entries)

    def expendituresModel(self):
        return self.__expendituresModel 

    def month(self):
        """
        Name of the tab's month.

        :return     str 
        """
        return self.__month 

    def monthIndex(self):
        """
        Index of the tab's month. January has 0, February has 1 etc.

        :return     int 
        """
        return self.__monthIndex

    def parseXMLtoModel(self, childList, appender):
        """
        Recursive function. Takes child from childList, creates
        appropriate item and appends it to the appender. 
        At the initial call, appender is a MonthTab's model.
        Later, appender is a CategoryItem. 

        :param      childList | list of xml children 
                    appender | items.Item
        """
        if issubclass(appender.__class__, QStandardItemModel):
            appender.clear()
            appender.setHorizontalHeaderLabels(_HEADERLABELS_)
        for child in childList:
            name = unicode(child.get('name'))
            value = str(child.get('value'))  
            if child.tag == 'model':
                appender.setValueItem(value)
                self.parseXMLtoModel(child.getchildren(), appender)
            elif child.tag == 'category':
                catItem = CategoryItem(name)
                appender.appendRow([catItem, SumItem(value), EmptyItem()])
                self.parseXMLtoModel(child.getchildren(), catItem)
            else:
                day = unicode(child.get('date'))
                dateItem = DateItem(day, self.monthIndex()+1, self.__mainWindow.year())
                appender.appendRow([
                    EntryItem(name), ExpenseItem(value), dateItem], False)

    def receiptsModel(self):
        return self.__receiptsModel 

    def setModels(self, filled):
        """ 
        Sets up the models for the expendituresView and receiptsView.
        Does not set the categoriesModel because expendituresModel and 
        receiptsModel are not yet filled with data when being loaded from 
        xml file (flag filled=False).
        """
        self.__expendituresModel = BalanceModel(
                self.__mainWindow, _EXPCATEGORIES_, filled)
        self.__receiptsModel = BalanceModel(
                self.__mainWindow, _RECCATEGORIES_, filled)
        

    def setViews(self):
        """
        Connects the tab's models to the  respective views. 
        Does some layout adjustments and sets up connections.
        Only called at initialization of MonthTab. 
        """
        self.expendituresView.setModel(self.__expendituresModel)
        self.receiptsView.setModel(self.__receiptsModel)
        for view in [self.expendituresView, self.receiptsView]:
            view.header().setResizeMode(QHeaderView.ResizeToContents)
            view.clicked.connect(self.__mainWindow.enableRemoveEntry)

    def writeToXML(self, xmlWriter, name, value, item):
        """
        Recursive function. Converts item and its children to XML.
        The initial call is from FinanceagerWindow.saveToXML(). 
        In this case, a MonthTab is passed as item. 
        In the next recursion run, the MonthTab's models are passed as items.
        Always pass the pointer to xmlWriter during recursion.
        The recursion is stopped when the EntryItem depth is reached.

        :param      xmlWriter | QtCore.QXmlStreamWriter
                    name, value | str 
                    item | items.Item 
        """
        xmlWriter.writeStartElement(item.xmlTag())
        xmlWriter.writeAttribute('name', name)
        xmlWriter.writeAttribute('value', unicode(value))
        if isinstance(item, EntryItem):
            xmlWriter.writeAttribute(
                    'date', unicode(item.parent().child(item.row(), 2).text()))
        elif isinstance(item, MonthTab):
            self.writeToXML(xmlWriter, 'expenditures', 
                    self.expendituresModel().value(), self.expendituresModel())
            self.writeToXML(xmlWriter, 'receipts', 
                    self.receiptsModel().value(), self.receiptsModel())
        elif not isinstance(item, EntryItem):
            for r in range(item.rowCount()):
                name = unicode(item.child(r, 0).text())
                value = str(item.child(r, 1).text())
                self.writeToXML(xmlWriter, name, value, item.child(r, 0))
        xmlWriter.writeEndElement()

    def xmlTag(self):
        return 'tab'
