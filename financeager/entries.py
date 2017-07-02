"""Defines Entries built from Items."""

from __future__ import unicode_literals
import datetime as dt

from schematics.types import ListType, ModelType, StringType, FloatType, DateType
from schematics.models import Model as SchematicsModel

# from .items import (CategoryItem, SumItem, NameItem, DateItem, ValueItem)
NameItem = StringType
CategoryItem = StringType
ValueItem = FloatType
SumItem = FloatType
DateItem = DateType


class Entry(SchematicsModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.lower()

class BaseEntry(Entry):
    name = NameItem(min_length=0)
    value = ValueItem()
    date = DateItem(default=dt.date.today())

    ITEM_TYPES = ["name", "value", "date"]

    @classmethod
    def from_tinydb_element(cls, element):
        """Create a BaseEntry from a TinyDB.database.Element. The element has
        to contain the fields `name` and `value`, `date` is optional."""
        return cls(element)

    def __str__(self):
        """Return a formatted string representing the entry."""
        capitalized_name = " ".join([s.capitalize() for s in self.name.split()])
        return "{:16.16} {:>8.2f} {}".format(capitalized_name, self.value,
                DateItem().to_primitive(self.date))

class CategoryEntry(Entry):
    name = CategoryItem(min_length=0)
    value = SumItem(default=0.0)
    entries = ListType(ModelType(BaseEntry), default=[])

    ITEM_TYPES = ["name", "sum", "empty"]

    def __str__(self):
        """Return a formatted string representing the entry. This is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented."""
        return "{:18} {:>8.2f}".format(self.name.capitalize(), self.value).ljust(38)
