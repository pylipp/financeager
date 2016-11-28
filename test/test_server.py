# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import Server, CONFIG_DIR
import os.path


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartServerTestCase, tests)))
    tests = [
            'test_entry_exists'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(ServerContextTestCase, tests)))
    return suite

class StartServerTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        server = Server()
        self.assertTrue(os.path.isdir(CONFIG_DIR))

class AddEntryToServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.server.add(name="Hiking boots", value="-111.11",
                category="outdoors")

    def test_entry_exists(self):
        self.assertIsNotNone(self.server._period._expenses_model.find_name_item(
            name="hiking boots", category="outdoors"))

class ServerContextTestCase(unittest.TestCase):
    def setUp(self):
        with Server() as server:
            server.add(name="Hiking boots", value="-111.11", category="outdoors")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(CONFIG_DIR, "2016.xml")))

if __name__ == '__main__':
    unittest.main()
