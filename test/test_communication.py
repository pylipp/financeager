import unittest
from datetime import date

from financeager.server import LocalServer
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
    def setUp(self):
        self.period = 0
        self.proxy = LocalServer(storage=MemoryStorage)
        communication.run(self.proxy, "add", name="pants", value=-99,
                period=self.period, category="clothes")

    def test_rm(self):
        response = communication.run(self.proxy, "rm", eid=1,
                period=self.period)
        self.assertEqual(response, "")

    def test_get(self):
        response = communication.run(self.proxy, "get", eid=1,
                period=self.period)
        self.assertEqual(response, """\
Name    : Pants
Value   : -99.0
Date    : {}
Category: Clothes""".format(date.today().strftime("%m-%d")))

    def test_erroneous_get(self):
        response = communication.run(self.proxy, "get", eid=0,
                period=self.period)
        self.assertTrue(response.startswith(
            communication.ERROR_MESSAGE.format("get", "")))

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
