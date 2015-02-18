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


from PyQt4.QtGui import (QDialog, QRegExpValidator, QDoubleValidator,
        QDialogButtonBox, QCompleter)
from PyQt4.QtCore import QRegExp, QDate, Qt
from . import loadUi


class NewEntryDialog(QDialog):
    """ 
    Dialog class for the input of new entry.
    The user has to give four inputs: 
        - a name via a QLineEdit. It is validated that the input length is
          non-zero. Also a completion list fed by previous made entries of the
          same month will pop up. 
        - a value via a QLineEdit. It is validated that the input is a double
          larger than 0.
        - a date via a QComboBox. The box is populated with all days that the
          current month holds (format: 1., 2., ..., 28., ...)
        - a category via a QComboBox. The box is populated with the
          categoriesModel of the current monthTab. 
    Submitting the entry is only enabled if all entries are valid.
    The parent passed at initialization is FinanceagerWindow.
    
    :param      parent | FinanceagerWindow 
    """

    def __init__(self, parent=None):
        super(NewEntryDialog, self).__init__(parent)
        loadUi(__file__, self)

        monthTab = parent.currentMonthTab()
        self.setWindowTitle('New Entry for \'%s\'' % monthTab.month())
        self.setFixedSize(self.size())
        strValidator = QRegExpValidator(QRegExp('.+'))
        self.nameEdit.setValidator(strValidator)
        completer = QCompleter(monthTab.entriesStringList())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.nameEdit.setCompleter(completer)
        validator = QDoubleValidator()
        validator.setBottom(0.01)
        self.expenseEdit.setValidator(validator)
        date = QDate(parent.year(), monthTab.monthIndex() + 1, 1)
        dateList = [ str(d+1)+'.' for d in range(date.daysInMonth()) ]
        self.dateCombo.addItems(dateList)
        self.categoryCombo.setModel(monthTab.categoriesModel())
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        # CONNECTIONS
        self.nameEdit.textEdited.connect(self.setOKButton)
        self.expenseEdit.textEdited.connect(self.setOKButton)
        
    def setOKButton(self):
        """
        Enables the Ok button if the given input to nameEdit and expenseEdit is valid.
        Prevents creating an entry without name or value.
        """
        self.okButton.setEnabled(self.nameEdit.hasAcceptableInput() and 
                self.expenseEdit.hasAcceptableInput())
