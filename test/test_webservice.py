#!/usr/bin/env python

import unittest
import os

from financeager.fflask import create_app, proxy
from financeager.config import CONFIG, CONFIG_DIR


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_print_rm'
        ,'test_add_get_rm_via_eid'
        ,'test_get_nonexisting_entry'
        ,'test_delete_nonexisting_entry'
        ]
    suite.addTest(unittest.TestSuite(map(WebserviceTestCase, tests)))
    return suite

class WebserviceTestCase(unittest.TestCase):
    def setUp(self):
        CONFIG["SERVICE:FLASK"]["debug"] = "yes"
        # FIXME does not use localhost!
        config = dict(
                debug=True,
                host="127.0.0.1:5000"
                )
        self.app = create_app(config=config).test_client()
        self.app.testing = True
        self.proxy = proxy()
        self.period = "0"

    def test_add_print_rm(self):
        add_response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food", repetitive=[])

        response = self.proxy.run("print", period=self.period)
        self.assertEqual(response["elements"][0]["name"], "cookies")
        self.assertEqual(len(response["elements"]), 1)

        response = self.proxy.run("rm", period=self.period, 
                eid=add_response["id"])
        self.assertEqual(response["id"], entry_id)

        response = self.proxy.run("list")
        self.assertIn(self.period, response["periods"])

    def test_add_get_rm_via_eid(self):
        entry_id = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets")

        response = self.proxy.run("get", period=self.period, eid=entry_id)
        self.assertEqual(response["element"]["name"], "donuts")

        response = self.proxy.run("rm", period=self.period, eid=entry_id)

        response = self.proxy.run("print", period=self.period)
        self.assertEqual(len(response["elements"]), 0)

    def test_get_nonexisting_entry(self):
        response = self.proxy.run("get", period=self.period, eid=-1)
        self.assertSetEqual({"error"}, set(response.keys()))

    def test_delete_nonexisting_entry(self):
        response = self.proxy.run("rm", period=self.period,
                name="something that won't be found", category="nowhere")
        self.assertSetEqual({"error"}, set(response.keys()))

    def tearDown(self):
        self.proxy.run("stop")
        filepath = os.path.join(CONFIG_DIR, "0.json")
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
