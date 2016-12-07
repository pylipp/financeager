# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import xml.etree.ElementTree as ET
from abc import ABCMeta, abstractmethod, abstractproperty
import Pyro4
from financeager.period import Period, XmlPeriod

CONFIG_DIR = os.path.expanduser("~/.config/financeager")

class Server(object):

    __metaclass__ = ABCMeta

    def __init__(self, period_name=None):
        self._running = True
        self._period_filepath = os.path.join(
                CONFIG_DIR, "{}.{}".format(
                    Period.DEFAULT_NAME if period_name is None else
                    period_name, self._file_suffix))
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

    @abstractproperty
    def _file_suffix(self):
        pass

    @property
    def running(self):
        return self._running

    @abstractmethod
    def run(self, command, **kwargs):
        if command == "stop":
            self._running = False
        else:
            command2method = {"add": "add_entry"}
            getattr(self._period, command2method[command])(**kwargs)

@Pyro4.expose
class XmlServer(Server):

    def __init__(self, period_name=None):
        super(XmlServer, self).__init__(period_name)
        self._period = XmlPeriod(period_name)
        self._read_period_from_file()

    @staticmethod
    def name(period_name):
        return "financeager_xml_server.{}".format(period_name)

    @property
    def _file_suffix(self):
        return "xml"

    def _read_period_from_file(self):
        if os.path.isfile(self._period_filepath):
            xml_tree = ET.parse(self._period_filepath)
            period_element = xml_tree.getroot()
            self._period.create_from_xml(period_element)

    def dump(self):
        period_element = self._period.convert_to_xml()
        xml_tree = ET.ElementTree(period_element)
        xml_tree.write(self._period_filepath, encoding="utf-8",
                xml_declaration=True)

    def run(self, command, **kwargs):
        """Call the server with any valid command line command. The underlying
        method of `Period` will be looked up and returned. This method is then
        supposed to be executed in the caller, passing keyword arguments.
        """
        super(XmlServer, self).run(command, **kwargs)
        if command != "stop":
            self.dump()
