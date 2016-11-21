#-*- coding: utf-8 -*-

from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtCore import QString
from financeager.entries import BaseEntry, CategoryEntry

class Model(QStandardItemModel):

    def __init__(self):
        super(QStandardItemModel, self).__init__()

    def add_entry(self, entry, category="Unspecified"):
        if isinstance(entry, CategoryEntry):
            if entry.name_item.data() not in self.category_entry_names:
                self.appendRow(entry.items)
        elif isinstance(entry, BaseEntry):
            self.add_entry(CategoryEntry(category))
            category_item = self.find_category_item(category)
            if category_item is not None:
                category_item.appendRow(entry.items)
                sum_item = category_item.entry.sum_item
                sum_item.update(entry.value_item)

    def category_entry_items(self, item_type):
        """yield: DataItem"""
        col = CategoryEntry.ITEM_TYPES.keys().index(item_type)
        for row in range(self.rowCount()):
            yield self.item(row, col)

    def base_entry_items(self, item_type):
        """yield: DataItem"""
        col = BaseEntry.ITEM_TYPES.keys().index(item_type)
        for category_item in self.category_entry_items("name"):
            for row in range(category_item.rowCount()):
                yield category_item.child(row, col)

    @property
    def category_entry_names(self):
        """yield: QString"""
        item_generator = self.category_entry_items("name")
        while True:
            try:
                yield item_generator.next().data()
            except StopIteration:
                break

    def find_category_item(self, category_name):
        """return: DataItem"""
        for category_item in self.category_entry_items("name"):
            if category_item.data() == QString(category_name.lower()):
                return category_item
        return None

    def category_sum(self, category):
        return 0.0
