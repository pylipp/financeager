import unittest
from datetime import date
from collections import defaultdict

from financeager import default_period_name
from financeager import communication, localserver, httprequests

from . import utils


def today():
    return date.today().strftime("%m-%d")


class CommunicationTestFixture(unittest.TestCase):
    def setUp(self):
        self.client = utils.Client()


class CommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        super().setUp()
        response = self.client.run(
            "add", name="pants", value=-99, category="clothes")
        self.assertEqual(response, {"id": 1})

    def test_remove(self):
        response = self.client.run("remove", eid=1)
        self.assertEqual(response, {"id": 1})

    def test_get(self):
        response = self.client.run("get", eid=1)
        self.assertDictEqual(
            response, {
                "element": {
                    "name": "pants",
                    "value": -99.0,
                    "date": today(),
                    "category": "clothes",
                }
            })

    def test_copy(self):
        period = default_period_name()
        response = self.client.run(
            "copy", eid=1, source_period=period, destination_period=period)
        self.assertEqual(response, {"id": 2})

    def test_update(self):
        response = self.client.run("update", eid=1, name="trousers")
        self.assertEqual(response, {"id": 1})
        response = self.client.run("get", eid=1)
        self.assertDictEqual(
            response, {
                "element": {
                    "name": "trousers",
                    "value": -99.0,
                    "date": today(),
                    "category": "clothes",
                }
            })

    def test_periods(self):
        response = self.client.run("periods")
        self.assertDictEqual(response, {"periods": [str(date.today().year)]})

    def test_list(self):
        response = self.client.run("list")
        self.assertNotEqual({}, response)

        response = self.client.run("list", filters={"date": "12-"})
        self.assertDictEqual(
            response,
            {"elements": {
                "standard": {},
                "recurrent": defaultdict(list),
            }})

    def test_stop(self):
        # For completeness, directly shutdown the localserver
        self.assertDictEqual(self.client.run("stop"), {})


class RecurrentEntryCommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        super().setUp()
        response = self.client.run(
            "add",
            name="retirement",
            value=567,
            category="income",
            frequency="monthly",
            start="01-01",
            table_name="recurrent")
        self.assertEqual(response, {"id": 1})

    def test_remove(self):
        response = self.client.run("remove", eid=1, table_name="recurrent")
        self.assertEqual(response, {"id": 1})

    def test_get(self):
        response = self.client.run("get", eid=1, table_name="recurrent")
        self.assertDictEqual(
            response, {
                "element": {
                    "name": "retirement",
                    "value": 567.0,
                    "frequency": "monthly",
                    "start": "01-01",
                    "end": "12-31",
                    "category": "income",
                }
            })

    def test_update(self):
        response = self.client.run(
            "update",
            eid=1,
            frequency="bimonthly",
            category="n.a.",
            table_name="recurrent")
        self.assertEqual(response, {"id": 1})
        response = self.client.run("get", eid=1, table_name="recurrent")
        self.assertDictEqual(
            response, {
                "element": {
                    "name": "retirement",
                    "value": 567.0,
                    "frequency": "bimonthly",
                    "start": "01-01",
                    "end": "12-31",
                    "category": "n.a.",
                }
            })


class CommunicationModuleTestCase(unittest.TestCase):
    def test_modules(self):
        module = communication.module("flask")
        self.assertEqual(module, httprequests)
        module = communication.module("none")
        self.assertEqual(module, localserver)


if __name__ == '__main__':
    unittest.main()
