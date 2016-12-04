#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from PyQt4.QtCore import QDate
import xml.etree.ElementTree as ET
from financeager.model import Model
from financeager.entries import BaseEntry

class Period(object):

    DEFAULT_NAME = QDate.currentDate().year()

    def __init__(self, name=None, xml_tree=None, models=None):
        self._name = "{}".format(Period.DEFAULT_NAME if name is None else name)
        self._earnings_model = None
        self._expenses_model = None
        if models is not None and len(models) == 2:
            self._earnings_model, self._expenses_model = models
        elif xml_tree is not None:
            self.create_from_xml(xml_tree)
        if self._earnings_model is None:
            self._earnings_model = Model()
        if self._expenses_model is None:
            self._expenses_model = Model()

    @property
    def name(self):
        return self._name

    def create_from_xml(self, xml_tree):
        root = xml_tree.getroot()
        earnings_element = root.find("earnings")
        if earnings_element is not None:
            self._earnings_model = Model(earnings_element)
        expenses_element = root.find("expenses")
        if expenses_element is not None:
            self._expenses_model = Model(expenses_element)
        self._name = root.get("name", Period.DEFAULT_NAME)

    def convert_to_xml(self):
        root = ET.Element("period", name=self._name)
        xml_tree = ET.ElementTree(root)
        for model_name in ["earnings", "expenses"]:
            model_element = ET.SubElement(root, model_name)
            getattr(self,
                    "_{}_model".format(model_name)).convert_to_xml(model_element)
        return xml_tree

    def add_entry(self, **kwargs):
        value = str(kwargs.pop("value"))
        category = kwargs.get("category")
        name = kwargs["name"]
        date = kwargs.get("date")
        if value.startswith("-"):
            self._expenses_model.add_entry(
                    BaseEntry(name, float(value[1:]), date), category=category)
        else:
            self._earnings_model.add_entry(
                    BaseEntry(name, float(value), date), category=category)
