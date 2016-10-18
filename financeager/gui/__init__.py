#!/usr/bin/python

""" Sub-package containing all user interface components for Financeager. """

# define authorship information
__authors__     = ['Philipp Metzner']
__author__      = ','.join(__authors__)
__credits__     = [
        ('Momenticons', 'Matte: Basic Icon Pack, CCA')
        ]
__copyright__   = 'Copyright (c) 2014'
__license__     = 'GPL'

# maintanence information
__maintainer__  = 'Philipp Metzner'
__email__       = 'beth.aleph@yahoo.de'


import os.path

import PyQt4.uic 
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QRegExpValidator
from PyQt4.QtCore import QDate, QRegExp, QLocale


_FONT_ = QtGui.QFont('Ubuntu')
_FONT_.setBold(True)

# default file name prefix 
_XMLFILE_ = 'financeager_year_'

from datetime import datetime 
_CURRENTMONTH_ = datetime.now().month - 1

# QDate is not affected by QLocale.setDefault() in main 
#_MONTHS_ = [unicode(QDate.longMonthName(m)) for m in range(1, 13)]
locale = QLocale()
_MONTHS_ = [unicode(locale.monthName(m)) for m in range(1, 13)]

# default category names used to set up models at start 
_EXPCATEGORIES_ = ['Bars, Party', 'Groceries', 'Household', 'Restaurants', 
        'Travelling', 'Clothes', 'Miscellaneous' ]

_RECCATEGORIES_ = [ 'Work', 'Gifts', 'Scholarships' ]

_HEADERLABELS_ = ['Name', 'Value', 'Date']

# global validator to check user given dates 
_DATEVALIDATOR_ = QRegExpValidator(QRegExp('\d{1,2}\.'))

def loadUi(modpath, widget):
    """
    Uses the PyQt4.uic.loadUi method to lead the input ui file associated
    with the given module path and widget class information on the input widget.
    
    :param modpath | str
    :param widget  | QWidget
    """
    # generate the uifile path
    basepath = os.path.dirname(modpath)
    basename = widget.__class__.__name__.lower()
    uifile   = os.path.join(basepath, 'ui/%s.ui' % basename)
    uipath   = os.path.dirname(uifile)

    # swap the current path to use the ui file's path
    currdir = QtCore.QDir.currentPath()
    QtCore.QDir.setCurrent(uipath)

    # load the ui
    PyQt4.uic.loadUi(uifile, widget)

    # reset the current QDir path
    QtCore.QDir.setCurrent(currdir)
