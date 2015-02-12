#!/usr/bin/python

""" Defines the SearchDialog Popup for the Financeager application. """

# define authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4.QtGui import QDialog, QStandardItem, QStandardItemModel,\
    QHeaderView, QDialogButtonBox 
from PyQt4.QtCore import Qt, QDate 
from items import ResultItem
from . import loadUi

class SearchDialog(QDialog):
    """
    SearchDialog class for the Financeager application.
    """

    def __init__(self, parent=None):
        """
        Loads the ui layout file. 
        Populates the model and does some layout adjustments. 
        
        :param      parent | FinanceagerWindow 
        """
        super(SearchDialog, self).__init__(parent)
        loadUi(__file__, self)

        self.__model = QStandardItemModel(self.tableView)
        self.__model.setHorizontalHeaderLabels(
                ['Name', 'Value', 'Date', 'Category'])
        self.tableView.setModel(self.__model)

        self.tableView.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.tableView.adjustSize()
        self.setFixedSize(self.size())
        self.buttonBox.button(QDialogButtonBox.Ok).setDefault(False)
        # CONNECTIONS
        self.findButton.clicked.connect(self.displaySearchResult)
        self.tableView.horizontalHeader().sectionClicked.connect(self.sortByColumn)

    def closeEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        #self.parentWidget().action_Statistics.setChecked(False)
        event.accept()

    def keyPressEvent(self, event):
        """ Reimplementation. Unchecks the action_Statistics of the MainWindow. """
        if event.key() == Qt.Key_Escape:
            pass
            #self.parentWidget().action_Statistics.setChecked(False)
        if event.key() == Qt.Key_Enter:
            return 
        super(SearchDialog, self).keyPressEvent(event)

    def displaySearchResult(self):
        """
        """
        pattern = unicode(self.lineEdit.text())
        self.setWindowTitle('Search for \'%s\'' % pattern)
        pattern = pattern.upper()
        monthsTabWidget = self.parent().monthsTabWidget 
        self.__model.clear()
        self.__model.setHorizontalHeaderLabels(
                ['Name', 'Value', 'Date', 'Category'])
        for m in range(12):
            for model in [monthsTabWidget.widget(m).expendituresModel(),
                    monthsTabWidget.widget(m).receiptsModel()]:
                for r in range(model.rowCount()):
                    category = model.item(r)
                    for e in range(category.rowCount()):
                        entry = category.child(e)
                        name = unicode(entry.text())
                        if name.upper().find(pattern) > -1:
                            nameItem = ResultItem(name)
                            nameItem.setCheckable(True)
                            value = category.child(e, 1).value()
                            # drop the trailing dot 
                            day = unicode(category.child(e, 2).text())[:-1]
                            date = QDate(self.parent().year(), m+1, int(day))
                            self.__model.appendRow([nameItem,
                                ResultItem(value), ResultItem(date),
                                ResultItem(category.text())])

    def sortByColumn(self, col):
        if col == 1:
            self.__model.setSortRole(Qt.UserRole + 1)
        self.__model.sort(col)
        #self.tableView.sortByColumn(col, Qt.AscendingOrder)
