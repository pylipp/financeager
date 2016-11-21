#-*- coding: utf-8 -*-

from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtCore import QString
from financeager.entries import BaseEntry, CategoryEntry
from financeager.items import ValueItem

class Model(QStandardItemModel):
    """Holds Entries in hierarchical order. First-level children are
    CategoryEntries, second-level children are BaseEntries. Generator methods
    are provided to iterate over these.
    """

    def __init__(self):
        super(QStandardItemModel, self).__init__()
        self.itemChanged.connect(self._update_sum_item)

    def add_entry(self, entry, category="Unspecified"):
        """Add a Category- or BaseEntry to the model.
        Category names are unique, i.e. a CategoryEntry is not skipped if one
        with identical name (case INsensitive) already exists.
        When adding a BaseEntry, the parent CategoryItem is created if it does
        not exist. If no category is specified, the BaseEntry is added to the
        'Unspecified' category. The corresponding sum item is updated.
        """
        if isinstance(entry, CategoryEntry):
            if entry.name_item.data() not in self.category_entry_names:
                self.appendRow(entry.items)
        elif isinstance(entry, BaseEntry):
            self.add_entry(CategoryEntry(category))
            category_item = self.find_category_item(category)
            category_item.appendRow(entry.items)
            self.itemChanged.emit(entry.value_item)

    def category_entry_items(self, item_type):
        """Generator iterating over first-level children (CategoryEntries) of
        the model. `item_type` is one of `CategoryEntry.ITEM_TYPES`.

        raises: KeyError if `item_type` not found.
        yields: CategoryItem, SumItem
        """
        col = CategoryEntry.ITEM_TYPES.keys().index(item_type)
        for row in range(self.rowCount()):
            yield self.item(row, col)

    def base_entry_items(self, item_type):
        """Generator iterating over second-level children (BaseEntries) of
        the model. `item_type` is one of `BaseEntry.ITEM_TYPES`.

        raises: KeyError if `item_type` not found.
        yields: NameItem, ValueItem, DateItem
        """
        col = BaseEntry.ITEM_TYPES.keys().index(item_type)
        for category_item in self.category_entry_items("name"):
            for row in range(category_item.rowCount()):
                yield category_item.child(row, col)

    @property
    def category_entry_names(self):
        """Convenience generator method yielding category names.

        yield: QString
        """
        item_generator = self.category_entry_items("name")
        while True:
            try:
                yield item_generator.next().data()
            except StopIteration:
                break

    def find_category_item(self, category_name):
        """Find CategoryItem by given `category_name` or return None if not
        found. The search is case insensitive.
        """
        for category_item in self.category_entry_items("name"):
            if category_item.data() == QString(category_name.lower()):
                return category_item
        return None

    def category_sum(self, category_name):
        """Return sum of category named `category_name`."""
        category_item = self.find_category_item(category_name)
        if category_item is not None:
            return category_item.entry.sum_item.value
        return 0.0

    def _update_sum_item(self, item):
        """Slot that updates the corresponding SumItem if a ValueItem is added
        or modified."""
        if isinstance(item, ValueItem):
            category_item = item.parent()
            if category_item is None:
                return
            col = BaseEntry.ITEM_TYPES.keys().index("value")
            new_sum = 0.0
            for row in range(category_item.rowCount()):
                new_sum += category_item.child(row, col).value
            sum_item = category_item.entry.sum_item
            sum_item.setText(QString("{}".format(new_sum)))
