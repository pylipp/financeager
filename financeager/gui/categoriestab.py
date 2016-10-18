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


from PyQt4.QtGui import QWidget, QButtonGroup, QMessageBox
from . import loadUi


class CategoriesTab(QWidget):
    """ 
    Widget for displaying the categories tab in the SettingsDialog. 
    This is embedded into the SettingsDialog. 
    The user can add or remove a category using several options. 
    For some reason, PyQt does not recognize QButtonGroup objects, hence they
    need to be defined explicitely. 
    Also, a reference to FinanceagerWindow is stored as private attribute
    self.__parent because later referencing does not work otherwise.
    """

    def __init__(self, parent=None):
        super(CategoriesTab, self).__init__(parent)
        loadUi(__file__, self)
        self.__parent = parent 

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
        Used for both populating the removeCategoryCombo and preventing the
        user from adding an already existing category. The latter is important
        in order to avoid ambiguities when removing a category. 

        :return     list(str)
        """
        categories = set()
        tabWidget = self.__parent.monthsTabWidget 
        for m in range(12):
            monthTab = tabWidget.widget(m)
            categories = categories.union(monthTab.categoriesStringList())
        categories = list(categories)
        categories.sort()
        return categories

    def checkForUniqueCategory(self, name):
        """
        Called from updateChangesToApply() to verify that the given category
        name is unique. Pops up a warning and resets newCategoryLineEdit if not. 

        :param      name | str 
        :return     uniqueCategory | bool 
        """
        #FIXME this also prevents adding a category that exists in any other month!
        if name in self.categoriesStringList():
            QMessageBox.warning(self.__parent, 'Name conflict', 
                    'This category name already exists. Please enter a unique name.')
            self.newCategoryLineEdit.setText('')
            self.newCategoryLineEdit.setFocus()
            return False 
        else: 
            return True 

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
                if self.checkForUniqueCategory(name):
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
