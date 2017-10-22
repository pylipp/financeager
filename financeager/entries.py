"""Defines Entries (data model rows built from fields)."""

from __future__ import unicode_literals

from .config import CONFIG
DATE_FORMAT = CONFIG["DATABASE"]["date_format"]


class Entry(object):
    """Base class. The name field is stored in lowercase, simplifying searching
    from the parent model."""

    def __init__(self, name, value, date):
        """:type name: str
        :type value: float or int
        :type date: str of valid format
        """
        self.name = name.lower()
        self.value = value
        self.date = date

class BaseEntry(Entry):
    """Innermost element of the Model, child of a CategoryEntry. Holds
    information on name, value, date and eid."""

    ITEM_TYPES = ["name", "value", "date"]

    NAME_LENGTH = 16
    VALUE_LENGTH = 8 # 00000.00
    VALUE_DIGITS = 2
    DATE_LENGTH = 5 # mm-dd
    SHOW_EID = True
    EID_LENGTH = 3 if SHOW_EID else 0
    # add spaces separating name/value, value/date and date/eid
    TOTAL_LENGTH = NAME_LENGTH + VALUE_LENGTH + DATE_LENGTH + EID_LENGTH + \
            3 if SHOW_EID else 2

    def __init__(self, name, value, date, eid=0):
        """:type eid: int
        """
        super().__init__(name, value, date)
        self.eid = eid

    @classmethod
    def from_tinydb(cls, element):
        """Create a BaseEntry from a TinyDB Element or a dict. In the first
        case, the entry eid is copied, otherwise it defaults to 0.
        """

        try:
            element.update({"eid": element.eid})
        except AttributeError:
            # element is dict, not tinydb.database.Element
            pass
        return cls(**element)

    def __str__(self):
        """Return a formatted string representing the entry. The value is
        rendered absolute."""
        capitalized_name = capitalize_words(self.name)
        string = "{name:{0}.{0}} {value:>{1}.{2}f} {date}".format(
                self.NAME_LENGTH, self.VALUE_LENGTH, self.VALUE_DIGITS,
                name=capitalized_name,
                value=abs(self.value),
                date=self.date
                )
        if self.SHOW_EID:
            string += " {1:{0}d}".format(self.EID_LENGTH, self.eid)
        return string

class CategoryEntry(Entry):
    """First child of the model, holding BaseEntries. Has a name and a value
    (i.e. the sum of its children's values)."""

    ITEM_TYPES = ["name", "sum", "empty"]
    DEFAULT_NAME = CONFIG["DATABASE"]["default_category"]

    BASE_ENTRY_INDENT = 2
    NAME_LENGTH = BaseEntry.NAME_LENGTH + BASE_ENTRY_INDENT
    TOTAL_LENGTH = BaseEntry.TOTAL_LENGTH + BASE_ENTRY_INDENT

    def __init__(self, name, value=0.0, entries=None):
        """:type entries: list[BaseEntry]"""
        super().__init__(name=name, value=value, date="")
        self.entries = entries or []

    def __str__(self):
        """Return a formatted string representing the entry including its
        children (i.e. BaseEntries). The category representation is supposed
        to be longer than the BaseEntry representation so that the latter is
        indented. The value is rendered absolute.
        """

        capitalized_name = capitalize_words(self.name)
        lines = [
                "{name:{0}.{0}} {value:>{1}.{2}f}".format(
                    self.NAME_LENGTH, BaseEntry.VALUE_LENGTH, BaseEntry.VALUE_DIGITS,
                    name=capitalized_name,
                    value=abs(self.value)
                    ).ljust(self.TOTAL_LENGTH)
                ]

        for entry in self.entries:
            lines.append("  " + str(entry))

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
