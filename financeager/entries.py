"""Data structures for smallest elements of frontend representation of database
query results."""

import time

from . import DEFAULT_BASE_ENTRY_SORT_KEY, POCKET_DATE_FORMAT


class Entry:
    """Base class. An entry represents a row in the table that is built from a
    Model.
    The name field is stored in lowercase, simplifying searching from the parent
    listing. The value is rendered absolute to simplify sorting."""

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
    DATE_FORMAT = "%y-%m-%d"
    DATE_LENGTH = 8  # yy-mm-dd
    SHOW_EID = True
    EID_LENGTH = 4 if SHOW_EID else 0
    # add spaces separating name/value, value/date and date/eid
    TOTAL_LENGTH = NAME_LENGTH + VALUE_LENGTH + DATE_LENGTH + EID_LENGTH + \
        3 if SHOW_EID else 2

    def __init__(self, name, value, date, eid=0):
        """:type eid: int or string, will be converted to int
        :type date: str of valid format
        """
        super().__init__(name, value)
        self.date = time.strftime(self.DATE_FORMAT,
                                  time.strptime(date, POCKET_DATE_FORMAT))
        self.eid = int(eid)

    def __str__(self):
        """Return a formatted string representing the entry."""

        string = "{name:{0}.{0}} {value:>{1}.{2}f} {date}".format(
            self.NAME_LENGTH,
            self.VALUE_LENGTH,
            self.VALUE_DIGITS,
            name=self.name.title(),
            value=self.value,
            date=self.date)
        if self.SHOW_EID:
            string += " {1:{0}d}".format(self.EID_LENGTH, self.eid)
        return string


class CategoryEntry(Entry):
    """First child of the listing, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""

    ITEM_TYPES = ["name", "sum", "empty"]
    DEFAULT_NAME = "unspecified"

    BASE_ENTRY_INDENT = 2
    NAME_LENGTH = BaseEntry.NAME_LENGTH + BASE_ENTRY_INDENT
    TOTAL_LENGTH = BaseEntry.TOTAL_LENGTH + BASE_ENTRY_INDENT

    def __init__(self, name, entries=None):
        """:type entries: list[BaseEntry]"""
        super().__init__(name=name or self.DEFAULT_NAME, value=0.0)

        self.entries = []
        if entries is not None:
            for base_entry in entries:
                self.append(base_entry)

    def append(self, base_entry):
        """Append a BaseEntry to the category and update the value."""
        self.entries.append(base_entry)
        self.value += base_entry.value

    def string(self,
               *,
               entry_sort=DEFAULT_BASE_ENTRY_SORT_KEY,
               total_listing_value=None):
        """Return a formatted string representing the entry including its
        children (i.e. BaseEntries). The category representation is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented.
        'entry_sort' determines the property according to which the list of base
        entries is sorted.
        If 'total_listing_value' is set, BaseEntries are not listed but instead
        the share in the total listing of the category is inserted.
        """
        percent = ""
        if total_listing_value is not None:
            percent = "{1:>{0}.1f}".format(
                BaseEntry.DATE_LENGTH, 100 * self.value / total_listing_value)

        lines = [
            "{name:{0}.{0}} {value:>{1}.{2}f} {percent}".format(
                self.NAME_LENGTH,
                BaseEntry.VALUE_LENGTH,
                BaseEntry.VALUE_DIGITS,
                name=self.name.title(),
                value=self.value,
                percent=percent,
            ).ljust(self.TOTAL_LENGTH)
        ]

        if total_listing_value is not None:
            return lines[0]

        sort_key = lambda e: getattr(e, entry_sort)
        for entry in sorted(self.entries, key=sort_key):
            lines.append(self.BASE_ENTRY_INDENT * " " + str(entry))

        return '\n'.join(lines)


def prettify(element, *, default_category):
    """Return element properties formatted as list. The type of the element
    (recurrent or standard) is inferred by the presence of the 'frequency'
    property.
    If the element's 'category' property is None, use 'default_category'.

    :type element: dict
    :type default_category: str
    """
    recurrent = "frequency" in element

    # Define order of listed properties
    if recurrent:
        properties = ("name", "value", "frequency", "start", "end", "category")
    else:
        properties = ("name", "value", "date", "category")
    longest_property_length = 0
    for p in properties:
        if len(p) > longest_property_length:
            longest_property_length = len(p)

    if element["category"] is None:
        element["category"] = default_category

    lines = []
    for p in properties:
        lines.append("{}: {}".format(
            p.capitalize().ljust(longest_property_length),
            str(element[p]).title()))

    return "\n".join(lines)
