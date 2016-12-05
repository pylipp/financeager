# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import XmlServer, CONFIG_DIR
import os.path
import subprocess
import signal
import socket
import sys


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartServerTestCase, tests)))
    tests = [
            'test_entry_exists',
            'test_period_name'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(ServerDumpTestCase, tests)))
    return suite

class StartServerTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        server = XmlServer()
        self.assertTrue(os.path.isdir(CONFIG_DIR))

class AddEntryToServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = XmlServer(0)
        self.dump_filepath = os.path.join(CONFIG_DIR, "0.xml")
        self.server.run("add", name="Hiking boots", value="-111.11",
                category="outdoors")

    def test_entry_exists(self):
        self.assertIsNotNone(self.server._period._expenses_model.find_name_item(
            name="hiking boots", category="outdoors"))

    def test_period_name(self):
        self.assertEqual("0", self.server._period.name)

    def tearDown(self):
        os.remove(self.dump_filepath)

class ServerDumpTestCase(unittest.TestCase):
    def setUp(self):
        server = XmlServer(42)
        self.dump_filepath = os.path.join(CONFIG_DIR, "42.xml")
        server.run("add", name="Hiking boots", value="-111.11", category="outdoors")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(self.dump_filepath))

    def tearDown(self):
        os.remove(self.dump_filepath)

if __name__ == '__main__':
    unittest.main()
