import unittest
from unittest import mock
import os.path

from financeager.offline import add, _load, recover, OfflineRecoveryError
from financeager.localserver import proxy as local_proxy


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_recover',
        'test_no_add',
        'test_no_recover',
        'test_failed_recover',
    ]
    suite.addTest(unittest.TestSuite(map(AddTestCase, tests)))
    return suite


class AddTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filepath = os.path.join(os.path.expanduser("~"), "offline_test.json")

    def test_add_recover(self):
        period_name = "123"
        kwargs = dict(name="money", value=111, period=period_name)
        self.assertTrue(add("add", offline_filepath=self.filepath, **kwargs))

        content = _load(self.filepath)

        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 1)
        data = content[0]
        self.assertEqual(data.pop("command"), "add")
        self.assertDictEqual(kwargs, data)

        proxy = local_proxy()
        self.assertTrue(recover(proxy, offline_filepath=self.filepath))

        element = proxy.run("get", eid=1, period=period_name)["element"]
        self.assertEqual(element["name"], "money")
        self.assertEqual(element["value"], 111)

    def test_no_add(self):
        self.assertFalse(add("print"))

    def test_no_recover(self):
        self.assertFalse(recover(None, offline_filepath=self.filepath))

    @mock.patch('financeager.offline.run')
    def test_failed_recover(self, run_mock):
        run_mock.side_effect = Exception()

        period_name = "123"
        kwargs = dict(name="money", value=111, period=period_name)
        self.assertTrue(add("add", offline_filepath=self.filepath, **kwargs))

        proxy = local_proxy()
        self.assertRaises(OfflineRecoveryError, recover, proxy,
                          offline_filepath=self.filepath)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


if __name__ == "__main__":
    unittest.main()
