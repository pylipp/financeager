#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from PyQt4.QtCore import QDate

class Period(object):

    DEFAULT_NAME = QDate.currentDate().year()

    def __init__(self, name=DEFAULT_NAME, *models):
        self._name = "{}".format(name)
        self._earnings_model = None
        self._expenses_model = None
        if len(models) == 2:
            self._earnings_model, self._expenses_model = models

    @property
    def name(self):
        return self._name
