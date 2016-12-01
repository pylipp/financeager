# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os.path
import xml.etree.ElementTree as ET
import Pyro4
from financeager.period import Period

CONFIG_DIR = os.path.expanduser("~/.config/financeager")

@Pyro4.expose
class Server(object):

    NAME_STUB = "financeager_server.{}"

    def __init__(self, period_name=None):
        self._running = True
        self._period = Period()
        self._period_filepath = os.path.join(CONFIG_DIR, "{}.xml".format(
            self._period.name if period_name is None else period_name))
        if not os.path.isdir(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self._read_period_from_file()

    def _read_period_from_file(self):
        if os.path.isfile(self._period_filepath):
            xml_tree = ET.parse(self._period_filepath)
            self._period.create_from_xml(xml_tree)

    @property
    def running(self):
        return self._running

    def dump(self):
        xml_tree = self._period.convert_to_xml()
        xml_tree.write(self._period_filepath, encoding="utf-8",
                xml_declaration=True)

    def run(self, command, **kwargs):
        """Call the server with any valid command line command. The underlying
        method of `Period` will be looked up and returned. This method is then
        supposed to be executed in the caller, passing keyword arguments.
        """
        if command == "stop":
            self._running = False
        else:
            command2method = {"add": "add_entry"}
            getattr(self._period, command2method[command])(**kwargs)
            self.dump()
