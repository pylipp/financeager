import unittest
from datetime import date

from financeager import default_period_name
from financeager.entries import BaseEntry
from financeager import communication, localserver, httprequests


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_rm',
        'test_get',
        'test_copy',
        'test_update',
        'test_print',
        'test_list',
        'test_stop',
    ]
    suite.addTest(unittest.TestSuite(map(CommunicationTestCase, tests)))
    tests = [
        'test_rm',
        'test_get',
        'test_update',
    ]
    suite.addTest(
        unittest.TestSuite(map(RecurrentEntryCommunicationTestCase, tests)))
    tests = ['test_modules']
    suite.addTest(unittest.TestSuite(map(CommunicationModuleTestCase, tests)))
    tests = [
        'test_date_format',
        'test_date_format_error',
        'test_filters',
        'test_filters_error',
        'test_default_category_filter',
    ]
    suite.addTest(unittest.TestSuite(map(PreprocessTestCase, tests)))
    return suite


def today():
    return date.today().strftime("%m-%d")


class CommunicationTestFixture(unittest.TestCase):
    def run_command(self, command, **kwargs):
        return communication.run(
            self.proxy, command, date_format=BaseEntry.DATE_FORMAT, **kwargs)

    def setUp(self):
        self.proxy = localserver.LocalServer()


class CommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        super().setUp()
        response = self.run_command(
            "add", name="pants", value=-99, category="clothes")
        self.assertEqual(response, "Added element 1.")

    def test_rm(self):
        response = self.run_command("rm", eid=1)
        self.assertEqual(response, "Removed element 1.")

    def test_get(self):
        response = self.run_command("get", eid=1)
        self.assertEqual(
            response, """\
Name    : Pants
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_copy(self):
        period = default_period_name()
        response = self.run_command(
            "copy", eid=1, source_period=period, destination_period=period)
        self.assertEqual(response, "Copied element 2.")

    def test_update(self):
        response = self.run_command("update", eid=1, name="trousers")
        self.assertEqual(response, "Updated element 1.")
        response = self.run_command("get", eid=1)
        self.assertEqual(
            response, """\
Name    : Trousers
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_list(self):
        response = self.run_command("list")
        self.assertEqual(response, "{}".format(date.today().year))

    def test_print(self):
        response = self.run_command("print")
        self.assertNotEqual("", response)

        response = self.run_command("print", filters=["date=12-"])
        self.assertEqual("", response)

    def test_stop(self):
        # For completeness, directly shutdown the localserver
        self.assertEqual(self.run_command("stop"), "")


class RecurrentEntryCommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        super().setUp()
        response = self.run_command(
            "add",
            name="retirement",
            value=567,
            category="income",
            frequency="monthly",
            start="01-01",
            table_name="recurrent")
        self.assertEqual(response, "Added element 1.")

    def test_rm(self):
        response = self.run_command("rm", eid=1, table_name="recurrent")
        self.assertEqual(response, "Removed element 1.")

    def test_get(self):
        response = self.run_command("get", eid=1, table_name="recurrent")
        self.assertEqual(
            response, """\
Name     : Retirement
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")

    def test_update(self):
        response = self.run_command(
            "update",
            eid=1,
            frequency="bimonthly",
            category="n.a.",
            table_name="recurrent")
        self.assertEqual(response, "Updated element 1.")
        response = self.run_command("get", eid=1, table_name="recurrent")
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


class PreprocessTestCase(unittest.TestCase):
    def test_date_format(self):
        data = {"date": "31.01."}
        communication._preprocess(data, date_format="%d.%m.")
        self.assertDictEqual(data, {"date": "01-31"})

    def test_date_format_error(self):
        data = {"date": "01-01"}
        self.assertRaises(
            communication.PreprocessingError,
            communication._preprocess,
            data,
            date_format="%d.%m")

    def test_filters(self):
        data = {"filters": ["name=italian", "category=Restaurants"]}
        communication._preprocess(data)
        self.assertEqual(data["filters"], {
            "name": "italian",
            "category": "restaurants"
        })

    def test_filters_error(self):
        data = {"filters": ["value-123"]}
        self.assertRaises(communication.PreprocessingError,
                          communication._preprocess, data)

    def test_default_category_filter(self):
        data = {"filters": ["category=unspecified"]}
        communication._preprocess(data)
        self.assertEqual(data["filters"], {"category": None})


if __name__ == '__main__':
    unittest.main()
