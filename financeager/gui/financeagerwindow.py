#!/usr/bin/python

""" Defines the main Financeager class. """

# authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox, QCheckBox 
from PyQt4.QtCore import pyqtSlot, QDate
from . import loadUi, _CURRENTMONTH_, _MONTHS_, _XMLFILE_
from monthtab import MonthTab 
from newentrydialog import NewEntryDialog 
from statisticswindow import StatisticsWindow 
from settingsdialog import SettingsDialog 
from searchdialog import SearchDialog 
from items import EntryItem, ExpenseItem, CategoryItem
from undocontainer import UndoContainer, ItemRow

class FinanceagerWindow(QtGui.QMainWindow):
    """ MainWindow class for the Financeager application. """
    
    def __init__(self, parent=None):
        super(FinanceagerWindow, self).__init__(parent)

        # load the ui
        loadUi(__file__, self)

        # define custom properties
        self.__year = None 
        # required in removeEntry() for index tracking
        self.__removeableIndex = None 
        # StatisticsWindow singleton
        self.__statWindow = None 
        # SearchWindow singleton
        self.__searchWindow = None
        # UndoContainer singleton 
        self.__undoContainer = UndoContainer(self)
        # holds boolean value whether file is automatically saved at exit
        self.__autoSave = False 
        self.__fileName = None 

        # adjust layout, i.e. set the MonthTabs
        for month in _MONTHS_:
            self.monthsTabWidget.addTab(MonthTab(self, month), month)
        # put the current month's tab to the front
        self.monthsTabWidget.setCurrentIndex(_CURRENTMONTH_)
        
        # if specified, load xml file from command line argument
        if QtCore.QCoreApplication.instance().argc() > 1:
            inputFile = QtCore.QCoreApplication.instance().argv()[1]
            if not os.path.isabs(inputFile):
                inputFile = os.path.sep.join([os.getcwd(), inputFile])
            if os.path.isfile(inputFile):
                self.loadYear(inputFile)
            else:
                print 'File does not exist: ' + inputFile

        # create connections
        self.action_New_Year.triggered.connect(self.newYear)
        self.action_New_Entry.triggered.connect(self.newEntry)
        self.action_Remove_Entry.triggered.connect(self.removeEntry)
        self.action_Undo.triggered.connect(self.__undoContainer.undoAction)
        self.action_Redo.triggered.connect(self.__undoContainer.redoAction)
        self.action_Load_Year.triggered.connect(self.loadYearFromUser)
        self.action_Statistics.toggled.connect(self.showStatistics)
        self.action_Settings.triggered.connect(self.showSettings)
        self.action_Search.toggled.connect(self.showSearchDialog)
        self.action_About.triggered.connect(self.showAbout)
        self.action_Quit.triggered.connect(self.close)
        
    
    def autoSave(self):
        return self.__autoSave 

    @pyqtSlot(bool)
    def setAutoSave(self, value):
        self.__autoSave = value 

    def closeEvent(self, event):
        """ 
        Reimplementation. 
        Asks the user whether to save the current year, then exits. 
        Also registers if the autoSave checkBox is checked.

        :param      event | QEvent emitted from close() signal
        """
        if self.__year is not None:
            if not self.__autoSave:
                question = QMessageBox(QMessageBox.Question, 
                        'Save file?', 'Do you want to save the current file to disk?')
                question.addButton(QMessageBox.Yes)
                question.addButton(QMessageBox.No)
                question.addButton(QMessageBox.Cancel)
                checkBox = QCheckBox('Always save at exit')
                checkBox.blockSignals(True)
                question.addButton(checkBox, QMessageBox.ActionRole)
                question.setDefaultButton(QMessageBox.Yes)
                question.exec_()
                buttonRole = question.buttonRole(question.clickedButton())
                if buttonRole == QMessageBox.YesRole or buttonRole == QMessageBox.NoRole:
                    self.__autoSave = checkBox.isChecked()
                    if buttonRole == QMessageBox.YesRole:
                        self.saveToXML()
                    event.accept()
                else: 
                    event.ignore()
            else:
                self.saveToXML()
                event.accept()
        else:
            event.accept()

    def currentMonthTab(self):
        """ 
        For simplicity. 
        :return     MonthTreeView 
        """
        return self.monthsTabWidget.currentWidget()

    def enableRemoveEntry(self, index):
        """
        Is called from the current month widget when an item is clicked. 
        Enables the remove entry action if item is of type entry or expense.

        :param      index | QModelIndex
        """
        item = index.model().itemFromIndex(index)
        self.action_Remove_Entry.setEnabled(isinstance(item.parent(), CategoryItem))
        self.__removeableIndex = index 

    @property 
    def fileName(self):
        return self.__fileName 

    @fileName.setter 
    def fileName(self, fileName):
        self.__fileName = fileName 

    def loadYear(self, inputFile):
        """
        Parses the inputFile and loads the content recursively.

        :param      inputFile | str 
        """
        import xml.etree.ElementTree as et 
        try:
            tree = et.parse(inputFile)
            root = tree.getroot()
        except (IOError, et.ParseError), err:
            QtGui.QMessageBox.warning(self, 'Error!', 
                    'An unexpected error occured during parsing the xml file: \n%s' % err)
            return 
        #FIXME just a work around because DateItems need the year
        self.__year = int(root.get('value'))
        for m, child in enumerate(root):
            #month = str(child.get('value'))
            # throws assertionerror if QLocale is not set correctly and shit
            #assert month == _MONTHS_[m]
            monthTab = self.monthsTabWidget.widget(m) 
            monthTab.parseXMLtoModel([child.getchildren()[0]], monthTab.expendituresModel())
            monthTab.parseXMLtoModel([child.getchildren()[1]], monthTab.receiptsModel())
            monthTab.expendituresView.expandAll()
            monthTab.receiptsView.expandAll()
        self.setYear(self.__year, inputFile)
        self.setAutoSave(root.get('autoSave') == 'True')
    
    def loadYearFromUser(self):
        """
        Asks the user to choose an appropriate xml file. 
        Calls loadYear() if inputFile is valid.
        """
        inputFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Load Year', 
            QtCore.QDir.currentPath(), 'xml file (*.xml)'))
        if inputFile:
            self.loadYear(inputFile)


    def newEntry(self):
        """ 
        Prompts the user with a dialog to input a new entry. 
        Writes the entry to the appropriate category in the current month tab. 
        """
        dialog = NewEntryDialog(self)
        if dialog.exec_():
            dialog.createNewEntry()
            
    def newYear(self):
        """
        Creates a new table with twelve empty MonthTabs. 
        Asks the user to give a year and if he wants to save the current year. 
        Kinda stupid. 
        """
        if self.__year is None:
            dialog = QtGui.QInputDialog(self)
            dialog.setWindowTitle('New Year')
            dialog.setLabelText('Enter a year: ')
            dialog.setInputMode(QtGui.QInputDialog.IntInput)
            dialog.setIntValue(QDate.currentDate().year())
            dialog.setIntMinimum(-4713) # valid QDate ranges
            dialog.setIntMaximum(11000000) 
            if dialog.exec_():
                year = dialog.intValue()
                #FIXME year must not be 0, invalid QDate otherwise
                for m in range(12):
                    self.monthsTabWidget.widget(m).setModels(filled=True)
                    self.monthsTabWidget.widget(m).setViews()
                self.setYear(year, _XMLFILE_ + str(year) + '.xml')
        # override if another year has already been loaded?
        else:
            answer = QtGui.QMessageBox.information(
                    self, 'New Year', 'Do you want to open a new year?',
                    QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                self.saveToXML()
                self.__year = None 
                self.newYear()
            return 

    def removeEntry(self):
        """ 
        Removes the selected entry from the model.
        Makes sure that item points to an ExpenseItem.
        Disables action_Remove_Entry if item at currentIndex does not suit.
        """
        index = self.__removeableIndex 
        model = index.model()
        entry = model.itemFromIndex(index.parent().child(index.row(), 0))
        expense = model.itemFromIndex(index.parent().child(index.row(), 1))
        date = model.itemFromIndex(index.parent().child(index.row(), 2))
        model.setSumItem(expense, 2*expense.value())
        removedRow = ItemRow(model.itemFromIndex(index.parent()), 
                (unicode(entry.text()), str(expense.value()), str(date.text())), 
                index.row())
        self.__undoContainer.addAction(removedRow)
        model.removeRow(index.row(), index.parent())
        #well, dirty hack...
        if self.currentMonthTab().expendituresView.model() == model:
            self.enableRemoveEntry(self.currentMonthTab().expendituresView.currentIndex())
        else:
            self.enableRemoveEntry(self.currentMonthTab().receiptsView.currentIndex())
        self.action_Undo.setEnabled(True)
        
    def saveToXML(self):
        """ Saves all the month tabs to an XML file. """
        xmlWriter = QtCore.QXmlStreamWriter()
        xmlWriter.setAutoFormatting(True)
        xmlFile = QtCore.QFile(self.fileName)

        if xmlFile.open(QtCore.QIODevice.WriteOnly) == False:
            QtGui.QMessageBox.warning(self, 'Error', 'Error opening file!')
        else:
            xmlWriter.setDevice(xmlFile)
            xmlWriter.writeStartDocument()
            xmlWriter.writeStartElement('root')
            xmlWriter.writeAttribute('name', 'year')
            xmlWriter.writeAttribute('value', str(self.__year))
            xmlWriter.writeAttribute('autoSave', str(self.__autoSave))
            for i in range(self.monthsTabWidget.count()):
                widget = self.monthsTabWidget.widget(i)
                widget.writeToXML(xmlWriter, 'month', widget.month(), widget)
            xmlWriter.writeEndElement()
            xmlWriter.writeEndDocument()
    
    def setYear(self, year, fileName):
        """ 
        Helper function. 
        Wraps some layout and action adjustments when new year is set. 
        """
        self.__year = year 
        self.fileName = fileName 
        self.action_New_Entry.setEnabled(True)
        self.action_Statistics.setEnabled(True)
        self.action_Search.setEnabled(True)
        self.action_Settings.setEnabled(True)
        self.setWindowTitle('Financeager - ' + str(self.__year))
        self.__statWindow = StatisticsWindow(self)
        self.__searchWindow = SearchDialog(self)
        self.monthsTabWidget.setCurrentIndex(_CURRENTMONTH_)

    def showAbout(self):
        """ Information window about the author, credits, etc. """
        pmpath = QtCore.QDir.currentPath() + \
                os.path.sep.join(['', 'src', 'resources', 'img', 'money.png'])
        messageBox = QtGui.QMessageBox(self)
        messageBox.setWindowTitle('About Financeager')
        messageBox.setText('Thank you for choosing Financeager.')
        messageBox.setInformativeText('Author: %s \nEmail: %s \nCredits: %s \n%s \n' % 
                (__author__, __email__, __credits__, __copyright__))
        messageBox.setIconPixmap(QtGui.QPixmap(pmpath))
        messageBox.exec_()

    def showSearchDialog(self, checked):
        """
        Shows the SearchDialog if it is hidden and hides it if it is
        currently shown. 
        """
        if self.__searchWindow is not None:
            if checked:
                self.__searchWindow.show()
            else:
                self.__searchWindow.hide()

    def showSettings(self):
        """
        Shows the SettingsDialog and sets up a connection to
        FinanceagerWindow's setAutoSave() slot. 
        Applies the requested changes if OK clicked. 
        """
        dialog = SettingsDialog(self)
        dialog.autoSaveSet[bool].connect(self.setAutoSave)
        if dialog.exec_():
            dialog.applyChanges()

    def showStatistics(self, checked):
        """
        Shows the StatisticsWindow if it is hidden and hides it if it is
        currently shown. 
        """
        if self.__statWindow is not None:
            if checked:
                self.__statWindow.show()
            else:
                self.__statWindow.hide()

    @property 
    def undoContainer(self):
        return self.__undoContainer

    def updateSearchDialog(self, item):
        """
        Called from BalanceModel. 
        Updates SearchDialog. 
        """
        if isinstance(item, (EntryItem, ExpenseItem)):
            self.__searchWindow.displaySearchResult()
            
    def year(self):
        """ :param  self.__year | int """
        return self.__year 
