"""Defines Entries (data model rows built from fields)."""

from __future__ import unicode_literals
import datetime as dt

from schematics.types import ListType, ModelType, StringType, FloatType, DateType
from schematics.models import Model as SchematicsModel

from .config import CONFIG


NameItem = StringType
CategoryItem = StringType
ValueItem = FloatType
SumItem = FloatType
DateItem = DateType


class Entry(SchematicsModel):
    """Base class storing the 'name' field in lowercase."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.name.lower()

class BaseEntry(Entry):
    """Innermost element of the Model, child of a CategoryEntry. Holds
    information on name, value and date."""
    name = NameItem(min_length=1)
    value = ValueItem()
    date = DateItem(default=dt.date.today())

    ITEM_TYPES = ["name", "value", "date"]

    def __str__(self):
        """Return a formatted string representing the entry. The value is
        rendered absolute."""
        capitalized_name = " ".join([s.capitalize() for s in self.name.split()])
        return "{:16.16} {:>8.2f} {}".format(capitalized_name, abs(self.value),
                self.date_str)

    @property 
    def date_str(self):
        """Convenience method to return formatted date."""
        return DateItem().to_primitive(self.date)


class CategoryEntry(Entry):
    """First child of the model, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""
    name = CategoryItem(min_length=1)
    value = SumItem(default=0.0)
    entries = ListType(ModelType(BaseEntry), default=[])

    ITEM_TYPES = ["name", "sum", "empty"]
    DEFAULT_NAME = CONFIG["DATABASE"]["default_category"]

    def __str__(self):
        """Return a formatted string representing the entry. This is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented. The value is rendered absolute."""
        # TODO append entries
        capitalized_name = " ".join([s.capitalize() for s in self.name.split()])
        return "{:18.18} {:>8.2f}".format(
                capitalized_name, abs(self.value)).ljust(38)


def create_base_entry(name, value, date=None):
    """Factory method for convenience."""
    data = {"name": name, "value": value}
    if date is not None:
        data["date"] = date
    return BaseEntry(data)
