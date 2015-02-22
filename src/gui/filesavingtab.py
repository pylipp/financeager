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


from PyQt4.QtGui import QWidget, QFileDialog 
from PyQt4.QtCore import QDir 
from . import loadUi


class FileSavingTab(QWidget):
    """ 
    Widget for displaying the file saving tab in the SettingsDialog.
    Parent is the FinanceagerWindow. 
    The user can put a path to save the current file to. Furthermore he can
    toggle the autosave option. 
    """

    def __init__(self, parent=None):
        super(FileSavingTab, self).__init__(parent)
        loadUi(__file__, self)
        self.fileNameLineEdit.setText(parent.fileName)
        self.fileNameLineEdit.selectAll()
        self.autoSaveCheckBox.setChecked(parent.autoSave())
        # CONNECTIONS
        self.browseButton.clicked.connect(self.getFileName)

    def getFileName(self):
        """
        Prompts a QFileDialog and asks user to give an xml file name. 
        Text of fileNameLineEdit is set to file name. 
        """
        fileName = unicode(QFileDialog.getSaveFileName(
                self.parent(), 'Please give a file name', 
                QDir.currentPath(), '*.xml'))
        if not fileName.endswith('.xml'):
            fileName += '.xml'
        self.fileNameLineEdit.setText(fileName)

    def updateChangesToApply(self, changes):
        """
        Checks the input of the fileNameLineEdit and the autoSaveCheckBox. 
        Creates a tuple consisting of a function string and a parameter 
        (name and boolean value, resp.)
        function:   'setFileName' | 'setAutoSave'
        parameter:  fileName | str 
                    autoSave | bool 
        The tuple is eventually evaluated by SettingsDialog.applyChanges() 
        if the dialog is not cancelled.

        :param      changes | set 
        """
        changes.add(('setFileName', unicode(self.fileNameLineEdit.text())))
        changes.add(('setAutoSave', self.autoSaveCheckBox.isChecked()))
