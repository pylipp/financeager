import unittest
from datetime import date

from financeager.server import LocalServer
from financeager.cli import _parse_command
from financeager import communication
from tinydb.storages import MemoryStorage

def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_rm',
            'test_get',
            'test_erroneous_get'
            ]
    suite.addTest(unittest.TestSuite(map(CommunicationTestCase, tests)))
    return suite

class CommunicationTestCase(unittest.TestCase):
    def run_command(self, args):
        cl_kwargs = _parse_command(args=args.split())
        command = cl_kwargs.pop("command")
        return communication.run(self.proxy, command, **cl_kwargs)

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
Category: Clothes""".format(date.today().strftime("%m-%d")))

    def test_erroneous_get(self):
        response = self.run_command("get 0")
        self.assertTrue(response.startswith(
            communication.ERROR_MESSAGE.format("get", "")))

    def test_update(self):
        response = self.run_command("update 1 -n trousers")
        self.assertEqual(response, "")
        response = self.run_command("get 1")
        self.assertEqual(response, """\
Name    : Trousers
Value   : -99.0
Date    : {}
Category: Clothes""".format(date.today().strftime("%m-%d")))

class RecurrentEntryCommunicationTestCase(unittest.TestCase):
    def setUp(self):
        self.period = 0
        self.proxy = LocalServer(storage=MemoryStorage)
        communication.run(self.proxy, "add", name="retirement money", value=567,
                period=self.period, category="income", frequency="monthly",
                start="01-01", table_name="recurrent")

    def test_get(self):
        response = communication.run(self.proxy, "get", eid=1,
                period=self.period, table_name="recurrent")
        self.assertEqual(response, """\
Name     : Retirement Money
Value    : 567.0
Frequency: Monthly
Start    : 01-01
End      : 12-31
Category : Income""")


if __name__ == '__main__':
    unittest.main()
