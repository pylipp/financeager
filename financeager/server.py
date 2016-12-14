# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import xml.etree.ElementTree as ET
from abc import ABCMeta, abstractmethod, abstractproperty
import Pyro4
from financeager.period import Period, TinyDbPeriod, XmlPeriod

CONFIG_DIR = os.path.expanduser("~/.config/financeager")

class Server(object):
    """Abstract class holding the database and communicated with via Pyro.

    The server creates a Period instance from the appropriate filepath in the
    config directory. It is typically launched at the initial `financeager`
    command line call and then runs in the background as a Pyro daemon.
    The `response` attribute can be used to access possible output data from
    querying commands (f.i. `find`).
    """

    __metaclass__ = ABCMeta

    def __init__(self, period_name=None):
        self._running = True
        self._period_filepath = os.path.join(
                CONFIG_DIR, "{}.{}".format(
                    Period.DEFAULT_NAME if period_name is None else
                    period_name, self._file_suffix))
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self._response = None

    @abstractproperty
    def _file_suffix(self):
        pass

    @property
    def running(self):
        return self._running

    @Pyro4.expose
    @property
    def response(self):
        return self._response

    @Pyro4.expose
    @response.setter
    def response(self, value):
        self._response = value

    @abstractmethod
    def run(self, command, **kwargs):
        """The method of `Period` corresponding to the given `command` is
        looked up and called. All `kwargs` are passed on. The return value is
        stored in the `response` attribute.
        Calling `stop` causes the Pyro daemon request loop to terminate.
        """
        if command == "stop":
            self._running = False
        else:
            command2method = {
                    "add": "add_entry",
                    "rm": "remove_entry",
                    "find": "find_entry",
                    "print": "all"
                    }
            self._response = getattr(self._period, command2method[command])(**kwargs)

@Pyro4.expose
class XmlServer(Server):
    """Server implementation holding a `XmlPeriod` database.

    The class explicitly loads the period at initialization and dumps it if a
    modifying command is called.

    NOTE: The development of this class is discontinued.
    """

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
        super(XmlServer, self).run(command, **kwargs)
        if command not in ["stop", "find"]:
            self.dump()

@Pyro4.expose
class TinyDbServer(Server):
    """Server implementation holding a `TinyDbPeriod` database.

    All database handling is taken care of in the underlying `TinyDbPeriod`.
    """

    def __init__(self, period_name=None):
        super(TinyDbServer, self).__init__(period_name)
        self._period = TinyDbPeriod(self._period_filepath)

    @property
    def _file_suffix(self):
        return "json"

    @staticmethod
    def name(period_name):
        return "financeager_tinydb_server.{}".format(period_name)

    def run(self, command, **kwargs):
        super(TinyDbServer, self).run(command, **kwargs)
