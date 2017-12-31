"""Defines Entries (data model rows built from fields)."""

from __future__ import unicode_literals
from datetime import datetime

from .import PERIOD_DATE_FORMAT


class Entry(object):
    """Base class. The name field is stored in lowercase, simplifying searching
    from the parent model. The value is rendered absolute to simplify sorting."""

    def __init__(self, name, value):
        """:type name: str
        :type value: float or int
        """
        self.name = name.lower()
        self.value = abs(value)


class BaseEntry(Entry):
    """Innermost element of the Model, child of a CategoryEntry. Holds
    information on name, value, date and eid."""

    ITEM_TYPES = ["name", "value", "date"]

    NAME_LENGTH = 16
    VALUE_LENGTH = 8  # 00000.00
    VALUE_DIGITS = 2
    DATE_FORMAT = "%m-%d"
    DATE_LENGTH = 5  # mm-dd
    SHOW_EID = True
    EID_LENGTH = 3 if SHOW_EID else 0
    # add spaces separating name/value, value/date and date/eid
    TOTAL_LENGTH = NAME_LENGTH + VALUE_LENGTH + DATE_LENGTH + EID_LENGTH + \
        3 if SHOW_EID else 2

    def __init__(self, name, value, date, eid=0):
        """:type eid: int
        :type date: str of valid format
        """
        super().__init__(name, value)
        self.date = datetime.strptime(
            date, PERIOD_DATE_FORMAT).strftime(self.DATE_FORMAT)
        self.eid = eid

    @classmethod
    def from_tinydb(cls, element):
        """Create a BaseEntry from a TinyDB Element. The ID is copied.
        """
        element.update({"eid": element.eid})
        return cls(**element)

    def __str__(self):
        """Return a formatted string representing the entry."""

        capitalized_name = capitalize_words(self.name)
        string = "{name:{0}.{0}} {value:>{1}.{2}f} {date}".format(
                self.NAME_LENGTH, self.VALUE_LENGTH, self.VALUE_DIGITS,
                name=capitalized_name,
                value=self.value,
                date=self.date
                )
        if self.SHOW_EID:
            string += " {1:{0}d}".format(self.EID_LENGTH, self.eid)
        return string


class CategoryEntry(Entry):
    """First child of the model, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""

    ITEM_TYPES = ["name", "sum", "empty"]
    DEFAULT_NAME = "unspecified"

    BASE_ENTRY_INDENT = 2
    NAME_LENGTH = BaseEntry.NAME_LENGTH + BASE_ENTRY_INDENT
    TOTAL_LENGTH = BaseEntry.TOTAL_LENGTH + BASE_ENTRY_INDENT

    BASE_ENTRY_SORT_KEY = "name"

    def __init__(self, name, entries=None):
        """:type entries: list[BaseEntry]"""
        super().__init__(name=name, value=0.0)

        self.entries = []
        if entries is not None:
            for base_entry in entries:
                self.append(base_entry)

    def append(self, base_entry):
        """Append a BaseEntry to the category and update the value."""
        self.entries.append(base_entry)
        self.value += base_entry.value

    def __str__(self):
        """Return a formatted string representing the entry including its
        children (i.e. BaseEntries). The category representation is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented.
        """

        capitalized_name = capitalize_words(self.name)
        lines = [
                "{name:{0}.{0}} {value:>{1}.{2}f}".format(
                    self.NAME_LENGTH, BaseEntry.VALUE_LENGTH,
                    BaseEntry.VALUE_DIGITS,
                    name=capitalized_name,
                    value=self.value
                    ).ljust(self.TOTAL_LENGTH)
                ]

        sort_key = lambda e: getattr(e, CategoryEntry.BASE_ENTRY_SORT_KEY)
        for entry in sorted(self.entries, key=sort_key):
            lines.append(self.BASE_ENTRY_INDENT * " " + str(entry))

        return '\n'.join(lines)


def prettify(element, recurrent=False):
    """Return element properties formatted as list.

    :type element: tinydb.database.Element
    """

    if recurrent:
        properties = ("name", "value", "frequency", "start", "end", "category")
    else:
        properties = ("name", "value", "date", "category")
    longest_property_length = 0
    for p in properties:
        if len(p) > longest_property_length:
            longest_property_length = len(p)

    lines = []
    for p in properties:
        lines.append("{}: {}".format(
            p.capitalize().ljust(longest_property_length),
            capitalize_words(element[p])
            ))

    return "\n".join(lines)


def capitalize_words(words):
    """Convenience method to capitalize all words of a phrase."""
    words = str(words)
    return " ".join([s.capitalize() for s in words.split()])
