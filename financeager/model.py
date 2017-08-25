#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import xml.etree.ElementTree as ET

from schematics.types import StringType, ListType, ModelType
from schematics.models import Model as SchematicsModel

from .entries import BaseEntry, CategoryEntry, create_base_entry


class Model(SchematicsModel):
    """Holds Entries in hierarchical order. First-level children are
    CategoryEntries, second-level children are BaseEntries. Generator methods
    are provided to iterate over these."""

    name = StringType(default="Model")
    categories = ListType(ModelType(CategoryEntry), default=[])

    def __init__(self, *args, **kwargs):
        super(SchematicsModel, self).__init__(*args, **kwargs)
        self._headers = [k.capitalize() for k in BaseEntry.ITEM_TYPES]

    @classmethod
    def from_tinydb(cls, elements, name=None):
        """Create model from tinydb.Elements or dict."""
        model = cls(raw_data={"name": name})
        for element in elements:
            category = element.pop("category", None)
            model.add_entry(BaseEntry(element), category_name=category)
        return model

    def __str__(self):
        """Format model (incl. name and header)."""
        result = ["{:^33}".format(self.name)]

        result.append("{:18} {:8} {:5}".format(*self._headers))

        for category in self.categories:
            result.append(str(category))

        return '\n'.join(result)

    def add_entry(self, entry, category_name=None):
        """Add a Category- or BaseEntry to the model.
        Category names are unique, i.e. a CategoryEntry is discarded if one
        with identical name (case INsensitive) already exists.
        When adding a BaseEntry, the parent CategoryEntry is created if it does
        not exist. If no category is specified, the BaseEntry is added to the
        default category. The CategoryEntry's value is updated."""

        if category_name is None:
            category_name = CategoryEntry.DEFAULT_NAME

        if isinstance(entry, CategoryEntry):
            if entry.name not in self.category_entry_names:
                self.categories.append(entry)
        elif isinstance(entry, BaseEntry):
            self.add_entry(CategoryEntry({"name": category_name}))
            category_item = self.find_category_entry(category_name)
            category_item.entries.append(entry)
            category_item.value += entry.value

    def remove_entry(self, entry, category):
        """Querying the given category, remove the first BaseEntry whose
        attributes are a superset of the attributes of `entry`.
        The corresponding CategoryEntry's value is updated. The method fails if
        the entry is not found.
        This method is to be removed in future releases."""

        item = self.find_base_entry(name=entry.name,
                date=entry.date_str, category=category)
        category_item = self.find_category_entry(category)
        category_item.value -= item.value
        category_item.entries.remove(item)

    def category_fields(self, field_type):
        """Generator iterating over the field specified by `field_type` of the
        first-level children (CategoryEntries) of the model.

        :param field_type: 'name' or 'value'

        raises: KeyError if `field_type` not found.
        yields: str or float
        """
        for category_entry in self.categories:
            yield getattr(category_entry, field_type)

    def base_entry_fields(self, field_type):
        """Generator iterating over the field specified by `field_type` of the
        second-level children (BaseEntries) of the model.

        :param field_type: 'name', 'value' or 'date'

        raises: KeyError if `field_type` not found.
        yields: str, float or datetime.date
        """
        for category_entry in self.categories:
            for base_entry in category_entry.entries:
                yield getattr(base_entry, field_type)

    @property
    def category_entry_names(self):
        """Convenience generator method yielding category names."""
        for category_name in self.category_fields("name"):
            yield category_name

    def find_category_entry(self, category_name):
        """Find CategoryEntry by given `category_name` or return None if not
        found. The search is case insensitive."""

        category_name = category_name.lower()
        for category_entry in self.categories:
            if category_entry.name == category_name:
                return category_entry
        return None

    def category_sum(self, category_name):
        """Return total value of category named `category_name`."""
        category_entry = self.find_category_entry(category_name)
        if category_entry is not None:
            return category_entry.value
        return 0.0

    def find_base_entry(self, **kwargs):
        """Find a BaseEntry by explicitely passing keyword arguments `name`
        and/or `value` and/or `date` and/or `category`. The first BaseEntry
        meeting the search requirements is returned. If no match is found,
        `None` is returned. The matching is performed case-INsensitive. If no
        category specified, the `CategoryEntry.DEFAULT_NAME` category is
        queried.
        kwargs values must be of type str or None."""

        category_name = kwargs.pop("category", CategoryEntry.DEFAULT_NAME)
        attributes = {v.lower() for v in kwargs.values() if v is not None}

        category_entry = self.find_category_entry(category_name)
        if category_entry is None:
            return None

        for base_entry in category_entry.entries:
            other_attributes = set()
            other_attributes.add(base_entry.name)
            other_attributes.add(base_entry.date_str)
            if attributes.issubset(other_attributes):
                return base_entry
        return None

    def convert_to_xml(self):
        model_element = ET.Element("model")
        if self.name is not None:
            model_element.set("name", self.name)
        for category_entry in self.categories:
            for entry in category_entry.entries:
                entry_element = ET.SubElement(
                        model_element,
                        "entry",
                        attrib=dict(
                            name=str(entry.name),
                            value=str(entry.value),
                            date=str(entry.date_str),
                            category=str(category_entry.name)
                            )
                        )
            entry_element.tail = "\n"
        model_element.text = "\n"
        model_element.tail = "\n"
        return model_element

    def create_from_xml(self, parent_element):
        self.name = parent_element.get("name")
        for child in parent_element:
            category_name = child.attrib.pop("category")
            self.add_entry(create_base_entry(child.attrib['name'],
                child.attrib['value'], child.attrib['date']), category_name)

    def total_value(self):
        """Return total value of the model."""
        result = 0.0
        for value in self.category_fields("value"):
            result += value
        return result


def prettify(elements, stacked_layout=False):
    """Sort the given elements (type tinydb.Element) by positive and negative
    value and return pretty string build from the corresponding Models.

    :param stacked_layout: If True, models are displayed one by one, else side by side"""

    if not elements:
        return ""

    earnings = []
    expenses = []

    for element in elements:
        if element["value"] > 0:
            earnings.append(element)
        else:
            expenses.append(element)

    model_earnings = Model.from_tinydb(earnings, "Earnings")
    model_expenses = Model.from_tinydb(expenses, "Expenses")

    if stacked_layout:
        return "{}\n\n{}\n\n{}".format(
                str(model_earnings),
                CategoryEntry.TOTAL_LENGTH * "-",
                str(model_expenses)
                )
    else:
        result = []
        models = [model_earnings, model_expenses]
        models_str = [str(m).splitlines() for m in models]
        for row in zip(*models_str):
            result.append(" | ".join(row))
        earnings_size = len(models_str[0])
        expenses_size = len(models_str[1])
        diff = earnings_size - expenses_size
        if diff > 0:
            for row in models_str[0][expenses_size:]:
                result.append(row + " | ")
        else:
            for row in models_str[1][earnings_size:]:
                result.append(CategoryEntry.TOTAL_LENGTH*" " + " | " + row)
        # add 3 to take central separator " | " into account
        result.append((2*CategoryEntry.TOTAL_LENGTH + 3) * "=")
        result.append(
                " | ".join(
                    [str(CategoryEntry(dict(
                        name="TOTAL", value=m.total_value())
                        ))
                        for m in models]
                    )
                )
        return '\n'.join(result)
