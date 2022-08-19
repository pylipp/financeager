"""Data structures for smallest elements of frontend representation of database
query results."""

import time

from . import POCKET_DATE_FORMAT


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

    DATE_FORMAT = "%y-%m-%d"

    def __init__(self, name, value, date, eid=0):
        """:type eid: int or string, will be converted to int
        :type date: str of valid format
        """
        super().__init__(name, value)
        self.date = time.strftime(
            self.DATE_FORMAT, time.strptime(date, POCKET_DATE_FORMAT)
        )
        self.eid = int(eid)


class CategoryEntry(Entry):
    """First child of the listing, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""

    DEFAULT_NAME = "unspecified"

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


def prettify(element, *, default_category):
    """Return element properties formatted as list. The type of the element (recurrent
    or standard) is inferred by the presence of the 'frequency' property.
    If the element's 'category' property is None, use 'default_category'.

    :type element: dict
    :type default_category: str
    """
    recurrent = "frequency" in element

    # Define order of listed properties
    if recurrent:
        properties = ("name", "value", "frequency", "start", "end", "category")
        longest_property_length = 9  # frequency
    else:
        properties = ("name", "value", "date", "category")
        longest_property_length = 8  # category

    if element["category"] is None:
        element["category"] = default_category

    lines = []
    for p in properties:
        lines.append(
            "{}: {}".format(
                p.capitalize().ljust(longest_property_length), str(element[p]).title()
            )
        )

    return "\n".join(lines)
