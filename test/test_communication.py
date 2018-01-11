import unittest
from datetime import date

from financeager.entries import BaseEntry
from financeager.server import LocalServer
from financeager.period import Period
from financeager.cli import _parse_command
from financeager import communication, server, fflask
from tinydb.storages import MemoryStorage


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_rm',
            'test_get',
            'test_erroneous_get',
            'test_copy',
            'test_update',
            'test_print',
            'test_print_with_sorting',
            'test_list',
            ]
    suite.addTest(unittest.TestSuite(map(CommunicationTestCase, tests)))
    tests = [
            'test_rm',
            'test_get',
            'test_update',
            ]
    suite.addTest(unittest.TestSuite(map(RecurrentEntryCommunicationTestCase, tests)))
    tests = ['test_modules']
    suite.addTest(unittest.TestSuite(map(CommunicationModuleTestCase, tests)))
    tests = [
        'test_filters',
        'test_filters_error',
    ]
    suite.addTest(unittest.TestSuite(map(PreprocessTestCase, tests)))
    return suite


def today():
    return date.today().strftime("%m-%d")


class CommunicationTestFixture(unittest.TestCase):
    def run_command(self, args):
        cl_kwargs = _parse_command(args=args.split())
        command = cl_kwargs.pop("command")
        return communication.run(self.proxy, command,
                                 date_format=BaseEntry.DATE_FORMAT, **cl_kwargs)


class CommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        self.proxy = LocalServer(storage=MemoryStorage)
        response = self.run_command("add pants -99 -c clothes")
        self.assertEqual(response, "")

    def test_rm(self):
        response = self.run_command("rm 1")
        self.assertEqual(response, "")

    def test_get(self):
        response = self.run_command("get 1")
        self.assertEqual(response, """\
Name    : Pants
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_erroneous_get(self):
        response = self.run_command("get 0")
        self.assertTrue(response.startswith(
            communication.ERROR_MESSAGE.format("get", "")))

    def test_copy(self):
        response = self.run_command("copy 1 -s {0} -d {0}".format(
            Period.DEFAULT_NAME))
        self.assertEqual(response, "")

    def test_update(self):
        response = self.run_command("update 1 -n trousers")
        self.assertEqual(response, "")
        response = self.run_command("get 1")
        self.assertEqual(response, """\
Name    : Trousers
Value   : -99.0
Date    : {}
Category: Clothes""".format(today()))

    def test_list(self):
        response = self.run_command("list")
        self.assertEqual(response, "{}".format(date.today().year))

    def test_print(self):
        response = self.run_command("print")
        self.assertNotIn(communication.ERROR_MESSAGE.format("print", ""),
                response)

    def test_print_with_sorting(self):
        response = self.run_command("add shirt -199 -c clothes -d 04-01")
        self.assertEqual(response, "")
        response = self.run_command("add lunch -20 -c food -d 04-01")
        self.assertEqual(response, "")

        response = self.run_command(
            "print --entry-sort value --category-sort name --stacked-layout")
        self.assertEqual(response,
"\
              Earnings               " + "\n\
Name               Value    Date  ID " + """

-------------------------------------

""" + "\
              Expenses               " + "\n\
Name               Value    Date  ID " + "\n\
Clothes              298.00          " + """
  Pants               99.00 {}   1
  Shirt              199.00 04-01   2""".format(today()) + "\n\
Food                  20.00          " + """
  Lunch               20.00 04-01   3""")


class RecurrentEntryCommunicationTestCase(CommunicationTestFixture):
    def setUp(self):
        self.proxy = LocalServer(storage=MemoryStorage)
        response = self.run_command(
                "add retirement 567 -c income -f monthly -s 01-01 -t recurrent")
        self.assertEqual(response, "")

    def test_rm(self):
        response = self.run_command("rm 1 -t recurrent")
        self.assertEqual(response, "")

    def test_get(self):
        response = self.run_command("get 1 -t recurrent")
        self.assertEqual(response, """\
Name     : Retirement
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")

    def test_update(self):
        response = self.run_command("update 1 -f bimonthly -c n.a. -t recurrent")
        self.assertEqual(response, "")
        response = self.run_command("get 1 -t recurrent")
        self.assertEqual(response, """\
Name     : Retirement
Value    : 567.0
Frequency: Bimonthly
Start    : 01-01
End      : 12-31
Category : N.a.""")


class CommunicationModuleTestCase(unittest.TestCase):
    def test_modules(self):
        module = communication.module("flask")
        self.assertEqual(module, fflask)
        module = communication.module("none")
        self.assertEqual(module, server)


class PreprocessTestCase(unittest.TestCase):
    def test_filters(self):
        data = {"filters": ["name=italian", "category=Restaurants"]}
        communication._preprocess(data)
        self.assertEqual(data["filters"],
                         {"name": "italian", "category": "restaurants"})

    def test_filters_error(self):
        data = {"filters": ["value-123"]}
        self.assertRaises(communication.PreprocessingError,
                          communication._preprocess, data)


if __name__ == '__main__':
    unittest.main()
