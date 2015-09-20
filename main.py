#!/usr/bin/python

""" Main entry point for the financeager application. """

# authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


from PyQt4 import QtGui 
from PyQt4.QtCore import QLocale

def main(argv=None):
    """
    Creates the main window for the financeager application and begins
    the QApplication if necessary. 
    """
    # locale settings. Default application language is English 
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))

    app = None 

    if not QtGui.QApplication.instance():
        app = QtGui.QApplication(argv)

    # create the main window
    from src.gui.financeagerwindow import FinanceagerWindow 
    window = FinanceagerWindow()
    window.show()
    
    if app:
        return app.exec_()
    
    return 0


if __name__ == '__main__':
    import sys 
    sys.exit(main(sys.argv))
