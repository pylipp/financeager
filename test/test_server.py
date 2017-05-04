# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.items import CategoryItem
from financeager.server import Server
from financeager.config import CONFIG_DIR
import os.path
from tinydb import database, storages


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_entry_exists',
            'test_period_name',
            'test_period_file_exists'
            ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
            'test_query_and_reset_response',
            'test_response_is_none'
            ]
    suite.addTest(unittest.TestSuite(map(FindEntryServerTestCase, tests)))
    return suite


class AddEntryToServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Server()
        cls.server.run("add", name="Hiking boots", value=-111.11,
                category="outdoors", period="0")

    def test_period_file_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(CONFIG_DIR, "0.json")))

    def test_entry_exists(self):
        self.assertIsInstance(self.server._periods["0"].find_entry(
            name="Hiking boots")[0], database.Element)

    def test_period_name(self):
        self.assertEqual("0", self.server._periods["0"]._name)

    @classmethod
    def tearDownClass(cls):
        cls.server.run("stop")
        os.remove(os.path.join(CONFIG_DIR, "0.json"))

class FindEntryServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server(storage=storages.MemoryStorage)
        self.period = "0"
        self.server.run("add", name="Hiking boots", value=-111.11,
                period=self.period)

    def test_query_and_reset_response(self):
        response = self.server.run("print", period=self.period, category=CategoryItem.DEFAULT_NAME)
        self.assertGreater(len(response), 0)
        self.assertIsInstance(response, dict)

    def test_response_is_none(self):
        self.server.run("rm", period=self.period, category=CategoryItem.DEFAULT_NAME)
        response = self.server.run("print", period=self.period, name="Hiking boots",
                category=CategoryItem.DEFAULT_NAME)
        self.assertListEqual([], response["elements"])

if __name__ == '__main__':
    unittest.main()
