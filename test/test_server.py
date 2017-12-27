# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.entries import CategoryEntry
from financeager.server import Server
from financeager.config import CONFIG_DIR
from financeager.period import PeriodException, Period


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_period_name',
        'test_period_file_exists',
        'test_list',
    ]
    suite.addTest(unittest.TestSuite(map(AddEntryToServerTestCase, tests)))
    tests = [
        'test_recurrent_entries',
    ]
    suite.addTest(unittest.TestSuite(map(RecurrentEntryServerTestCase, tests)))
    tests = [
        'test_get_period',
        'test_query_and_reset_response',
        'test_response_is_none',
        'test_update',
        'test_copy',
        'test_unsuccessful_copy',
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

    def test_period_name(self):
        self.assertEqual("0", self.server._periods["0"]._name)

    def test_list(self):
        response = self.server.run("list")
        self.assertListEqual(response["periods"], ["0"])

    @classmethod
    def tearDownClass(cls):
        cls.server.run("stop")
        os.remove(os.path.join(CONFIG_DIR, "0.json"))


class RecurrentEntryServerTestCase(unittest.TestCase):

    def setUp(self):
        self.server = Server(storage=storages.MemoryStorage)
        self.period = "2000"
        self.entry_id = self.server.run("add", name="rent", value=-1000,
                table_name="recurrent", frequency="monthly", start="01-02",
                end="07-01", period=self.period)["id"]

    def test_recurrent_entries(self):
        elements = self.server.run("print", period=self.period,
                name="rent")["elements"]["recurrent"][self.entry_id]
        self.assertEqual(len(elements), 6)


class FindEntryServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server(storage=storages.MemoryStorage)
        self.period = "0"
        self.entry_id = self.server.run("add", name="Hiking boots", value=-111.11,
                period=self.period)["id"]

    def test_get_period(self):
        period = self.server._get_period(self.period)
        self.assertEqual(period.name, self.period)

        another_period_name = "foo"
        period = self.server._get_period(another_period_name)
        self.assertEqual(period.name, another_period_name)

        period = self.server._get_period(None)
        self.assertEqual(period.name, str(Period.DEFAULT_NAME))

    def test_query_and_reset_response(self):
        category = CategoryEntry.DEFAULT_NAME
        response = self.server.run("print", period=self.period,
                category=category)
        self.assertGreater(len(response), 0)
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response["elements"], dict)
        self.assertIsInstance(response["elements"]["standard"], dict)
        self.assertIsInstance(response["elements"]["recurrent"], dict)

    def test_response_is_none(self):
        response = self.server.run("get", period=self.period, eid=self.entry_id)
        self.assertIn("element", response)
        self.assertEqual(response["element"].eid, self.entry_id)

        response = self.server.run("rm", period=self.period, eid=self.entry_id)
        self.assertEqual(response["id"], self.entry_id)

        response = self.server.run("print", period=self.period, name="Hiking boots",
                category=CategoryEntry.DEFAULT_NAME)
        self.assertDictEqual(response["elements"]["standard"], {})
        self.assertDictEqual(response["elements"]["recurrent"], {})

    def test_update(self):
        new_category = "Outdoorsy shit"
        self.server.run("update", eid=self.entry_id, period=self.period,
                category=new_category)
        element = self.server.run("get", eid=self.entry_id,
                period=self.period)["element"]
        self.assertEqual(element["category"], new_category.lower())

if __name__ == '__main__':
    unittest.main()
