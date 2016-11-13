#-*- coding: utf-8 -*-

from PyQt4.QtGui import QStandardItemModel

class Model(QStandardItemModel):

    def __init__(self):
        super(QStandardItemModel, self).__init__()

    def add_entry(self, entry, category):
        pass

    @property
    def categories(self):
        yield None

    def category_sum(self, category):
        return 0.0
