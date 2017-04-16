# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.items import CategoryItem
from financeager.entries import BaseEntry
from financeager.server import XmlServer, CONFIG_DIR, TinyDbServer
import os.path
import subprocess
import signal
import socket
import sys
import tinydb


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartXmlServerTestCase, tests)))
    tests = [
            'test_entry_exists',
            'test_period_name'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToXmlServerTestCase, tests)))
    suite.addTest(unittest.TestSuite(map(AddEntryToTinyDbServerTestCase, tests)))
    tests = [
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(XmlServerDumpTestCase, tests)))
    tests = [
            'test_query_and_reset_response',
            'test_response_is_none'
            ]
    suite.addTest(unittest.TestSuite(map(FindEntryTinyDbServerTestCase, tests)))
    return suite

class StartXmlServerTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        server = XmlServer()
        self.assertTrue(os.path.isdir(CONFIG_DIR))

class AddEntryToXmlServerTestCase(unittest.TestCase):
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

class XmlServerDumpTestCase(unittest.TestCase):
    def setUp(self):
        server = XmlServer(42)
        self.dump_filepath = os.path.join(CONFIG_DIR, "42.xml")
        server.run("add", name="Hiking boots", value=-111.11, category="outdoors")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(self.dump_filepath))

    def tearDown(self):
        os.remove(self.dump_filepath)

class AddEntryToTinyDbServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = TinyDbServer(0)
        self.dump_filepath = os.path.join(CONFIG_DIR, "0.json")
        self.server.run("add", name="Hiking boots", value=-111.11,
                category="outdoors")

    def test_entry_exists(self):
        self.assertIsInstance(self.server._period.find_entry(
            name="Hiking boots")[0], tinydb.database.Element)

    def test_period_name(self):
        self.assertEqual("0", self.server._period.name)

    def tearDown(self):
        os.remove(self.dump_filepath)

class FindEntryTinyDbServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = TinyDbServer(0)
        self.dump_filepath = os.path.join(CONFIG_DIR, "0.json")
        self.server.run("add", name="Hiking boots", value=-111.11)

    def test_query_and_reset_response(self):
        self.server.run("print", category=CategoryItem.DEFAULT_NAME)
        response = self.server.response
        self.assertIsNone(self.server.response)
        self.assertGreater(len(response), 0)
        self.assertIsInstance(response, str)

    def test_response_is_none(self):
        self.server.run("rm", category=CategoryItem.DEFAULT_NAME)
        self.server.run("print", name="Hiking boots",
                category=CategoryItem.DEFAULT_NAME)
        self.assertEqual(0, len(self.server.response))

    def tearDown(self):
        os.remove(self.dump_filepath)

if __name__ == '__main__':
    unittest.main()
