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


from PyQt4.QtGui import QDialog 
from . import loadUi


class ButtonGroupTest(QDialog):
    """ Dialog class to administer the settings of Financeager. """

    def __init__(self, parent=None):
        super(ButtonGroupTest, self).__init__(parent)
        loadUi(__file__, self)
        print self.radioButton.isChecked()
        print self.buttonGroup.buttons()
        print self.buttonGroup_2.buttons()
