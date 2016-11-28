# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import xml.etree.ElementTree as ET
from financeager.period import Period

CONFIG_DIR = os.path.expanduser("~/.config/financeager")

class Server(object):

    def __init__(self, name=None):
        self._name = name
        self._period_filepath = os.path.join(CONFIG_DIR, "2016.xml")
        self._period = None
        self._read_period_from_file()

    def _read_period_from_file(self):
        if os.path.isdir(CONFIG_DIR):
            if os.path.isfile(self._period_filepath):
                xml_tree = ET.parse(self._period_filepath)
                self._period = Period(xml_tree=xml_tree)
                return
        else:
            os.makedirs(CONFIG_DIR)
        self._period = Period()

    def __getattr__(self, name):
        """Call the server with any valid command line command. The underlying
        method of `Period` will be looked up and returned. This method is then
        supposed to be executed in the caller, passing keyword arguments.
        """
        command2method = {"add": "add_entry"}
        return getattr(self._period, command2method[name])
