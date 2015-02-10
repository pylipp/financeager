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


from PyQt4.QtGui import QWidget, QButtonGroup
from . import loadUi


class CategoriesTab(QWidget):
    """ Widget for displaying the categories tab in the SettingsDialog. """

    def __init__(self, parent=None):
        super(CategoriesTab, self).__init__(parent)
        loadUi(__file__, self)
        # for some reason, PyQt does not recognize QButtonGroup objects
        # need to be defined explicitely
        self.removeFromMonthButtons = QButtonGroup()
        self.removeFromMonthButtons.addButton(self.removeAllMonthsButton)
        self.removeFromMonthButtons.addButton(self.removeAllMonthsFromNowButton)
        self.removeFromMonthButtons.addButton(self.removeCurrentMonthButton)
        self.addToMonthButtons = QButtonGroup()
        self.addToMonthButtons.addButton(self.addAllMonthsButton)
        self.addToMonthButtons.addButton(self.addAllMonthsFromNowButton)
        self.addToMonthButtons.addButton(self.addCurrentMonthButton)
        self.expAndRecButtons = QButtonGroup()
        self.expAndRecButtons.addButton(self.expendituresButton)
        self.expAndRecButtons.addButton(self.receiptsButton)
        self.removeCategoryCombo.addItems(self.categoriesStringList())
        # CONNECTIONS
        self.addCategoryGroup.clicked.connect(self.newCategoryLineEdit.setFocus)

    def categoriesStringList(self):
        """
        Returns a sorted list of all the categories that occur in the parentwidget's 
        (== FinanceagerWindow's) tabs.

        :return     list(str)
        """
        categories = set()
        tabWidget = self.parentWidget().monthsTabWidget 
        for m in range(12):
            monthTab = tabWidget.widget(m)
            categories = categories.union(monthTab.categoriesStringList())
        categories = list(categories)
        categories.sort()
        return categories

    def updateChangesToApply(self, changes):
        """
        Checks for checked GroupBoxes. 
        Creates a tuple consisting of a function string and a tuple that contains 
        name, typ and option. Those three are fetched from the tab's widgets. 
        function:   'addCategory' | 'removeCategory' 
        name:       new category name | category to delete 
        option:     0 (all months) | 1 (all months from now) | 2 (current month)
        typ:        0 (expenditure) | 1 (receipt)
        The tuple is eventually evaluated by SettingsDialog.applyChanges() 
        if the dialog is not cancelled.

        :param      changes | set 
        """
        if self.addCategoryGroup.isChecked():
            name = unicode(self.newCategoryLineEdit.text()).strip()
            if len(name):
                typ = self.expAndRecButtons.buttons().index(
                        self.expAndRecButtons.checkedButton())
                option = self.addToMonthButtons.buttons().index(
                        self.addToMonthButtons.checkedButton())
                changes.add(('addCategory', (name, typ, option)))
        if self.removeCategoryGroup.isChecked():
            name = unicode(self.removeCategoryCombo.currentText())
            option = self.removeFromMonthButtons.buttons().index(
                    self.removeFromMonthButtons.checkedButton())
            changes.add(('removeCategory', (name, option)))
