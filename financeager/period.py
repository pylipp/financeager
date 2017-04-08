#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
from dateutil import rrule
from datetime import datetime as dt

from PyQt5.QtCore import QDate
import xml.etree.ElementTree as ET
from tinydb import TinyDB, Query, where
from tinydb.database import Element
from tinydb.queries import QueryImpl

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
        super(TinyDbPeriod, self).__init__(filepath, default_table="standard")
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

        repetitive_args = kwargs.get("repetitive", False)
        if repetitive_args:
            frequency = repetitive_args[0].lower()
            start = str(DateItem())
            if len(repetitive_args) > 1:
                start = repetitive_args[1]
            end = None
            if len(repetitive_args) > 2:
                end = repetitive_args[2]
            self.table("repetitive").insert(
                    dict(
                        name=name, value=value, category=category,
                        frequency=frequency, start=start, end=end
                        ))
        else:
            self.insert(
                    dict(
                        name=name, value=value, date=date, category=category))

    def _search_all_tables(self, query_impl):
        elements = self.search(query_impl)

        if len(self.tables()) > 1:
            repetitive_elements = self.table("repetitive").search(query_impl)

            for element in repetitive_elements:
                elements.extend(list(self._create_repetitive_elements(element)))

        return elements

    def _create_repetitive_elements(self, element):
        name = element["name"]
        value = element["value"]
        category = element.get("category")
        frequency = element["frequency"].upper()
        start = element["start"]
        end = element.get("end")

        if end is None:
            end = dt.now()
            last_second = dt(int(self._name), 12, 31, 23, 59, 59)
            if end > last_second:
                end = last_second
        else:
            end = dt.strptime(end, DateItem.FORMAT)

        rule = rrule.rrule(
                getattr(rrule, frequency),
                dtstart=dt.strptime(start, DateItem.FORMAT),
                until=end
                )

        for date in rule:
            element_name = name
            if frequency == "MONTHLY":
                element_name = "{} {}".format(name, date.strftime("%B").lower())
            yield Element(dict(
                name=element_name, value=value, category=category,
                date=date.strftime(DateItem.FORMAT)
                ))

    def find_entry(self, **kwargs):
        query_impl = None
        for kwarg, value in kwargs.items():
            if isinstance(value, str):
                value = value.lower()
            if query_impl is None:
                query_impl = (getattr(Query(), kwarg) == value)
            else:
                query_impl &= (getattr(Query(), kwarg) == value)
        elements = self._search_all_tables(query_impl)
        return elements

    def remove_entry(self, **kwargs):
        entry = self.find_entry(**kwargs)
        if entry:
            self.remove(eids=[entry[0].eid])

    def _create_models(self, date=None):
        models = []
        for name, comparator in zip(["Earnings", "Expenses"], ["__gt__", "__lt__"]):
            query_impl = getattr(where("value"), comparator)(0)
            if date is not None:
                query_impl &= (Query().date.matches("{}-*".format(date)))
            elements = self._search_all_tables(query_impl)
            models.append(Model.from_tinydb(elements, name))
        return models

    def print_entries(self, date=None, stacked_layout=False):
        models = self._create_models(date=date)
        if stacked_layout:
            models_str = [str(model) for model in models]
            return "{}\n\n{}\n\n{}".format(
                    models_str[0], 38*"-", models_str[1]
                    )
        else:
            result = []
            models_str = [str(model).splitlines() for model in models]
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
            return '\n'.join(result)
