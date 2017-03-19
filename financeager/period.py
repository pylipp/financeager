#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from PyQt5.QtCore import QDate
import xml.etree.ElementTree as ET
from tinydb import TinyDB, Query, where
from tinydb.queries import QueryImpl
import os.path
from financeager.model import Model
from financeager.entries import BaseEntry
from financeager.items import DateItem

class Period(object):

    DEFAULT_NAME = QDate.currentDate().year()

    def __init__(self, name=None):
        self._name = "{}".format(Period.DEFAULT_NAME if name is None else name)

    @property
    def name(self):
        return self._name

class XmlPeriod(Period):

    def __init__(self, name=None, xml_element=None, models=None):
        super(XmlPeriod, self).__init__(name)
        # TODO store models in dict
        self._earnings_model = None
        self._expenses_model = None
        if models is not None and len(models) == 2:
            self._earnings_model, self._expenses_model = models
        elif xml_element is not None:
            self.create_from_xml(xml_element)
        if self._earnings_model is None:
            self._earnings_model = Model(name="earnings")
        if self._expenses_model is None:
            self._expenses_model = Model(name="expenses")

    def create_from_xml(self, xml_element):
        for model_element in xml_element.findall("model"):
            name = model_element.get("name")
            if name == "earnings":
                self._earnings_model = Model(model_element)
            elif name == "expenses":
                self._expenses_model = Model(model_element)
        self._name = xml_element.get("name", Period.DEFAULT_NAME)

    def convert_to_xml(self):
        period_element = ET.Element("period", name=self._name)
        period_element.text = "\n"
        for model_name in ["earnings", "expenses"]:
            model_element = getattr(self,
                    "_{}_model".format(model_name)).convert_to_xml()
            period_element.append(model_element)
        return period_element

    def add_entry(self, **kwargs):
        value = str(kwargs.pop("value"))
        category = kwargs.get("category")
        name = kwargs["name"]
        date = kwargs.get("date")
        if value.startswith("-"):
            self._expenses_model.add_entry(
                    BaseEntry(name, value, date), category=category)
        else:
            self._earnings_model.add_entry(
                    BaseEntry(name, value, date), category=category)

class TinyDbPeriod(TinyDB, Period):

    def __init__(self, filepath):
        super(TinyDbPeriod, self).__init__(filepath)
        self._name = os.path.splitext(os.path.basename(filepath))[0]

    def add_entry(self, **kwargs):
        value = kwargs["value"]
        name = kwargs["name"].lower()
        date = kwargs.get("date")
        if date is None:
            date = str(DateItem())
        category = kwargs.get("category")
        if category is not None:
            category = category.lower()
        self.insert(dict(name=name, value=value, date=date, category=category))

    def find_entry(self, **kwargs):
        entry = Query()
        query_impl = QueryImpl(lambda _: True, 0)
        for kwarg, value in kwargs.items():
            if isinstance(value, str):
                value = value.lower()
            query_impl = query_impl & (getattr(entry, kwarg) == value)
        result = self.search(query_impl)
        return result

    def remove_entry(self, **kwargs):
        entry = self.find_entry(**kwargs)
        if entry:
            self.remove(eids=[entry[0].eid])

    def __str__(self):
        models = []
        for name, comparator in zip(["Earnings", "Expenses"], ["__gt__", "__lt__"]):
            elements = self.search(getattr(where("value"), comparator)(0))
            model = Model.from_tinydb(elements, name)
            models.append(str(model).splitlines())
        result = []
        for row in zip(*models):
            result.append(" | ".join(row))
        earnings_size = len(models[0])
        expenses_size = len(models[1])
        diff = earnings_size - expenses_size
        if diff > 0:
            for row in models[0][expenses_size:]:
                result.append(row + " | ")
        else:
            for row in models[1][earnings_size:]:
                result.append(38*" " + " | " + row)
        return '\n'.join(result)
