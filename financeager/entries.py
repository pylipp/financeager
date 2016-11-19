"""Defines Entries built from Items."""

from items import (CategoryItem, SumItem, EmptyItem, NameItem, DateItem,
        ValueItem)
from abc import ABCMeta
from collections import OrderedDict

class Entry(object):
    """Abstract base class for all entries.

    An Entry is a wrapper around several items and allows simple access of
    corresponding item data. It can be visualized as a row in the data sheet.
    """
    __metaclass__ = ABCMeta

    #FIXME This would be prettier when using ordered kwargs as introduced in 3.6
    def __init__(self, *args):
        self._items = []
        # expand if args are omitted
        args_list = list(args) + (len(self.ITEM_TYPES) - len(args)) * [None]
        # FIXME this iteration is actually required only once when creating a
        # class not every time an instance is created. Use factory instead?
        # BaseEntry = type("BaseEntry", (Entry,), {methods})
        for type_, arg in zip(self.ITEM_TYPES.keys(), args_list):
            ItemClass = self.ITEM_TYPES[type_]
            kwargs = dict(entry=self)
            if arg is not None:
                kwargs["data"] = arg
            self._items.append(ItemClass(**kwargs))

    def __getattr__(self, name):
        """Reimplementation for accessing item member data."""
        return self._items[self.ITEM_TYPES.keys().index(name)].data()

    @property
    def items(self):
        return self._items

class BaseEntry(Entry):
    """Wrapper around a Name-, Value-, DateItem tuple."""

    ITEM_TYPES = OrderedDict((
        ("name", NameItem), ("value", ValueItem), ("date", DateItem)))

class CategoryEntry(Entry):
    """Wrapper around a Category- and SumItem tuple."""

    ITEM_TYPES = OrderedDict((
        ("name", CategoryItem), ("sum", SumItem), ("empty", EmptyItem)))
