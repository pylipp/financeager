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
        - a value via a QDoubleSpinBox. The input value has to be larger than 0.
        - a date via a QDateEdit. The valid date range are the days of the
          month of the currently selected monthTab.
        - a category via a QComboBox. The box is populated with the
          categoriesModel of the current monthTab. 
    Submitting the entry is only enabled if all entries are valid.
    The parent passed at initialization is FinanceagerWindow.
    
    :param      parent | FinanceagerWindow 
    """

    def __init__(self, parent=None):
        super(NewEntryDialog, self).__init__(parent)
        loadUi(__file__, self)

        # General window settings
        monthTab = parent.currentMonthTab()
        self.setWindowTitle('New Entry for \'%s\'' % monthTab.month())
        self.setFixedSize(self.size())

        # Entry name LineEdit settings
        strValidator = QRegExpValidator(QRegExp('.+'))
        self.nameLineEdit.setValidator(strValidator)
        completer = QCompleter(monthTab.entriesStringList())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.nameLineEdit.setCompleter(completer)

        # DateEdit settings
        date = QDate(parent.year(), monthTab.monthIndex() + 1, 1)
        self.dateEdit.setDateRange(date, 
                QDate(date.year(), date.month(), date.daysInMonth()))
        self.dateEdit.setDate(date)
        self.dateEdit.setCalendarPopup(True)

        # CategoryComboBox settings
        self.categoryComboBox.setModel(monthTab.categoriesModel())

        # OK PushButton settings
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.okButton.setEnabled(False)
        # CONNECTIONS
        self.nameLineEdit.textEdited.connect(self.setOKButton)
        
    def setOKButton(self):
        """
        Enables the Ok button if the given input to nameLineEdit is valid.
        Prevents creating an entry without name.
        """
        self.okButton.setEnabled(self.nameLineEdit.hasAcceptableInput())

    def categoryString(self):
        """
        Convenience method. Returns string representation of the currently
        selected item of the CategoryComboBox.

        :return     category | str 
        """
        return unicode(self.categoryComboBox.currentText())

    def nameString(self):
        """
        Convenience method. Returns content of NameLineEdit as string.

        :return     name | str 
        """
        return unicode(self.nameLineEdit.text())

    def valueString(self):
        """
        Convenience method. Returns value of ValueDoubleSpinBox as string. 

        :return     value | str 
        """
        return str(self.valueDoubleSpinBox.value())

    def date(self):
        """
        :return     date | QDate 
        """
        return self.dateEdit.date()
