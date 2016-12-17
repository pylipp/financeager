#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from PyQt4.QtCore import QDate
import xml.etree.ElementTree as ET
from tinydb import TinyDB, Query, where
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
        name = kwargs["name"]
        date = kwargs.get("date")
        if date is None:
            date = str(DateItem())
        category = kwargs.get("category")
        self.insert(dict(name=name, value=value, date=date, category=category))

    def find_entry(self, **kwargs):
        entry = Query()
        kwarg, value = kwargs.popitem()
        query_impl = (getattr(entry, kwarg) == value)
        for kwarg in kwargs:
            query_impl = query_impl & (getattr(entry, kwarg) == kwargs[kwarg])
        result = self.search(query_impl)
        return result

    def remove_entry(self, **kwargs):
        entry = self.find_entry(**kwargs)
        if entry:
            self.remove(eids=[entry[0].eid])

    def __str__(self):
        result = []
        for name, comparator in zip(["Earnings", "Expenses"], ["__gt__", "__lt__"]):
            elements = self.search(getattr(where("value"), comparator)(0))
            model = Model.from_tinydb(elements, name)
            result.append(str(model))
        return result
