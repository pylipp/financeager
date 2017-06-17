import unittest
import os.path

import json 

from financeager.config import CONFIG, CONFIG_DIR
from financeager.offline import add, _load


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_add'
            ]
    suite.addTest(unittest.TestSuite(map(AddTestCase, tests)))
    return suite


class AddTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        CONFIG["DATABASE"]["offline_backup"] = "offline_test"
        cls.filepath = os.path.join(CONFIG_DIR, "offline_test.json")

    def test_add(self):
        kwargs = dict(name="money", value=111, period=123)
        add("add", **kwargs)
        
        content = _load(self.filepath)

        self.assertIsInstance(content, list)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]["command"], "add")
        self.assertDictEqual(kwargs, content[0]["kwargs"])

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


if __name__ == "__main__":
    unittest.main()
