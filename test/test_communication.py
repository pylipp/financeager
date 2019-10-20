import unittest
from datetime import date

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
        self.assertEqual(response, "Added element 1.")

    def test_remove(self):
        response = self.client.run("remove", eid=1)
        self.assertEqual(response, "Removed element 1.")

    def test_get(self):
        response = self.client.run("get", eid=1)
        self.assertEqual(
            response, """\
Name    : Pants
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_copy(self):
        period = default_period_name()
        response = self.client.run(
            "copy", eid=1, source_period=period, destination_period=period)
        self.assertEqual(response, "Copied element 2.")

    def test_update(self):
        response = self.client.run("update", eid=1, name="trousers")
        self.assertEqual(response, "Updated element 1.")
        response = self.client.run("get", eid=1)
        self.assertEqual(
            response, """\
Name    : Trousers
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_periods(self):
        response = self.client.run("periods")
        self.assertEqual(response, "{}".format(date.today().year))

    def test_list(self):
        formatting_options = dict(
            stacked_layout=False, entry_sort="name", category_sort="value")
        response = self.client.run("list", **formatting_options)
        self.assertNotEqual("", response)

        response = self.client.run(
            "list", filters={"date": "12-"}, **formatting_options)
        self.assertEqual("", response)

    def test_stop(self):
        # For completeness, directly shutdown the localserver
        self.assertEqual(self.client.run("stop"), "")


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
        self.assertEqual(response, "Added element 1.")

    def test_remove(self):
        response = self.client.run("remove", eid=1, table_name="recurrent")
        self.assertEqual(response, "Removed element 1.")

    def test_get(self):
        response = self.client.run("get", eid=1, table_name="recurrent")
        self.assertEqual(
            response, """\
Name     : Retirement
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")

    def test_update(self):
        response = self.client.run(
            "update",
            eid=1,
            frequency="bimonthly",
            category="n.a.",
            table_name="recurrent")
        self.assertEqual(response, "Updated element 1.")
        response = self.client.run("get", eid=1, table_name="recurrent")
        self.assertEqual(
            response, """\
Name     : Retirement
Value    : 567.0
Frequency: Bimonthly
Start    : 01-01
End      : 12-31
Category : N.A.""")


class CommunicationModuleTestCase(unittest.TestCase):
    def test_modules(self):
        module = communication.module("flask")
        self.assertEqual(module, httprequests)
        module = communication.module("none")
        self.assertEqual(module, localserver)


if __name__ == '__main__':
    unittest.main()
