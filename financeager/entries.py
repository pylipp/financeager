"""Defines Entries built from Items."""

from __future__ import unicode_literals

from .items import (CategoryItem, SumItem, EmptyItem, NameItem, DateItem,
        ValueItem)
from abc import ABCMeta


class Entry(object):
    """Abstract base class for all entries.

    An Entry is a wrapper around several items and allows simple access of
    corresponding item data. It can be visualized as a row in the data sheet.
    Subclasses have to contain members named `self._foo_item` of type
    `FooItem`.
    """
    __metaclass__ = ABCMeta

    def __getattr__(self, name):
        """Reimplementation for accessing an item member."""
        name = name.replace("_item", "")
        return self.__dict__["_{}_item".format(name)]

    @property
    def items(self):
        return [getattr(self, attr) for attr in self.ITEM_TYPES]

class BaseEntry(Entry):
    """Wrapper around a Name-, Value-, DateItem tuple."""

    ITEM_TYPES = ["name", "value", "date"]

    def __init__(self, name, value, date=None):
        self._name_item = NameItem(name, entry=self)
        self._value_item = ValueItem(value, entry=self)
        self._date_item = DateItem(date, entry=self)

    @classmethod
    def from_tinydb_element(cls, element):
        """Create a BaseEntry from a TinyDB.database.Element. The element has
        to contain the fields `name` and `value`, `date` is optional."""
        base_entry = cls(element["name"], element["value"], element.get("date"))
        return base_entry

    def __str__(self):
        """Return a formatted string representing the entry."""
        attributes = [getattr(self, attrib).text() for attrib in self.ITEM_TYPES]
        return "{:16.16} {:>8} {}".format(*attributes)

class CategoryEntry(Entry):
    """Wrapper around a Category- and SumItem tuple."""

    ITEM_TYPES = ["name", "sum", "empty"]

    def __init__(self, name, sum=0.0):
        self._name_item = CategoryItem(name, entry=self)
        self._sum_item = SumItem(sum, entry=self)
        self._empty_item = EmptyItem(entry=self)

    def __str__(self):
        """Return a formatted string representing the entry. This is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented."""
        attributes = [getattr(self, attrib).text() for attrib in self.ITEM_TYPES]
        return "{:18} {:>8} {:10}".format(*attributes)
