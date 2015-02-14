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


from PyQt4.QtGui import QDialog, QRegExpValidator, QDoubleValidator, QDialogButtonBox 
from PyQt4.QtCore import QRegExp, QDate
from . import loadUi, _CURRENTMONTH_
from calendar import monthrange


class NewEntryDialog(QDialog):
    #TODO implement autocomletion for name lineEdit.
    """ Dialog class for the input of new entry. """

    def __init__(self, parent=None):
        super(NewEntryDialog, self).__init__(parent)
        loadUi(__file__, self)

        month = parent.currentMonthTab().month()
        self.setWindowTitle('New Entry for \'%s\'' % month)
        self.setFixedSize(self.size())
        strValidator = QRegExpValidator(QRegExp('.+'))
        self.nameEdit.setValidator(strValidator)
        validator = QDoubleValidator()
        validator.setBottom(0.01)
        self.expenseEdit.setValidator(validator)
        dateList = [ str(d+1)+'.' for d in range(monthrange(
            int(parent.year()), _CURRENTMONTH_)[1]) ]
        self.dateCombo.addItems(dateList)
        self.categoryCombo.setModel(parent.currentMonthTab().categoriesModel())
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
