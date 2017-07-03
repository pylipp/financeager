#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import (QVariant, Qt)
from tinydb import where
import xml.etree.ElementTree as ET

from schematics.types import StringType, ListType, ModelType
from schematics.models import Model as SchematicsModel 

from financeager.entries import BaseEntry, CategoryEntry, create_base_entry
from financeager.items import ValueItem, CategoryItem


class Model(SchematicsModel):
    """Holds Entries in hierarchical order. First-level children are
    CategoryEntries, second-level children are BaseEntries. Generator methods
    are provided to iterate over these.
    When a `root_element` (type `ET.Element`) is passed at initialization, the
    model is built from it.
    """

    name = StringType(default="Model")
    categories = ListType(ModelType(CategoryEntry), default=[])

    def __init__(self, *args, **kwargs):
        super(SchematicsModel, self).__init__(*args, **kwargs)
        self._headers = [k.capitalize() for k in BaseEntry.ITEM_TYPES]

    @classmethod
    def from_tinydb(cls, elements, name=None):
        model = cls(raw_data={"name": name})
        for element in elements:
            category = element.pop("category", None)
            model.add_entry(BaseEntry(element), category=category)
        return model

    def __str__(self):
        result = ["{:^38}".format(self.name)]

        result.append("{:18} {:8} {:10}".format(*self._headers))

        for category in self.categories:
            result.append(str(category))
            for entry in category.entries:
                result.append("  " + str(entry))

        return '\n'.join(result)

    def add_entry(self, entry, category=None):
        """Add a Category- or BaseEntry to the model.
        Category names are unique, i.e. a CategoryEntry is not skipped if one
        with identical name (case INsensitive) already exists.
        When adding a BaseEntry, the parent CategoryItem is created if it does
        not exist. If no category is specified, the BaseEntry is added to the
        default category. The corresponding sum item is updated.
        """
        if category is None:
            category = CategoryItem.DEFAULT_NAME
        if isinstance(entry, CategoryEntry):
            if entry.name not in self.category_entry_names:
                self.categories.append(entry)
        elif isinstance(entry, BaseEntry):
            self.add_entry(CategoryEntry({"name": category}))
            category_item = self.find_category_item(category)
            category_item.entries.append(entry)
            category_item.value += entry.value

    def remove_entry(self, entry, category):
        """Querying the given category, remove the first base entry whose
        attributes are a superset of the attributes of `entry`.
        The corresponding SumItem is updated.
        """
        item = self.find_name_item(name=entry.name,
                date=entry.date_str, category=category)
        category_item = self.find_category_item(category)
        category_item.value -= item.value
        category_item.entries.remove(item)
        #TODO remove category bc empty ?

    def category_entry_items(self, item_type):
        """Generator iterating over first-level children (CategoryEntries) of
        the model. `item_type` is one of `CategoryEntry.ITEM_TYPES`.

        raises: KeyError if `item_type` not found.
        yields: CategoryItem, SumItem
        """
        for category in self.categories:
            yield getattr(category, item_type)

    def base_entry_items(self, item_type):
        """Generator iterating over second-level children (BaseEntries) of
        the model. `item_type` is one of `BaseEntry.ITEM_TYPES`.

        raises: KeyError if `item_type` not found.
        yields: NameItem, ValueItem, DateItem
        """
        for category_entry in self.categories:
            for base_entry in category_entry.entries:
                yield getattr(base_entry, item_type)

    @property
    def category_entry_names(self):
        """Convenience generator method yielding category names.
        """
        for category_name in self.category_entry_items("name"):
            yield category_name

    def find_category_item(self, category_name):
        """Find CategoryItem by given `category_name` or return None if not
        found. The search is case insensitive.
        """
        category_name = category_name.lower()
        for category in self.categories:
            if category.name == category_name:
                return category
        return None

    def category_sum(self, category_name):
        """Return sum of category named `category_name`."""
        category_item = self.find_category_item(category_name)
        if category_item is not None:
            return category_item.value
        return 0.0

    def _update_sum_item(self, item):
        """Slot that updates the corresponding SumItem if a ValueItem is added
        or modified."""
        if isinstance(item, ValueItem):
            category_item = item.parent()
            if category_item is None:
                return
            col = list(BaseEntry.ITEM_TYPES).index("value")
            new_sum = 0.0
            for row in range(category_item.rowCount()):
                new_sum += category_item.child(row, col).value
            sum_item = category_item.entry.sum_item
            sum_item.setText(QString("{}".format(new_sum)))

    def find_name_item(self, **kwargs):
        """Find a NameItem by explicitely passing keyword arguments `name`
        and/or `value` and/or `date` and/or `category`. The first NameItem
        meeting the search requirements is returned. If no match is found,
        `None` is returned. The matching is performed case-INsensitive. If no
        category specified, the `CategoryItem.DEFAULT_NAME` category is
        queried.
        kwargs values must be of type str.
        """
        category_name = kwargs.pop("category", CategoryItem.DEFAULT_NAME)
        attributes = {v.lower() for v in kwargs.values() if v is not None}
        category_item = self.find_category_item(category_name)
        if category_item is None:
            return None
        for base_entry in category_item.entries:
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
        result = 0.0
        for item in self.category_entry_items("value"):
            result += item
        return result


def prettify(elements, stacked_layout=False):
    if not elements:
        return ""

    query = where("value") > 0
    earnings = []
    expenses = []

    for element in elements:
        if query(element):
            earnings.append(element)
        else:
            expenses.append(element)

    model_earnings = Model.from_tinydb(earnings, "Earnings")
    model_expenses = Model.from_tinydb(expenses, "Expenses")

    if stacked_layout:
        return "{}\n\n{}\n\n{}".format(
                str(model_earnings), 38*"-", str(model_expenses)
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
                result.append(38*" " + " | " + row)
        result.append(79*"=")
        result.append(
                " | ".join(
                    [str(CategoryEntry(name="TOTAL", sum=m.total_value()))
                        for m in models]
                    )
                )
        return '\n'.join(result)
