#!/usr/bin/env python

import unittest
import time
import os

from financeager.fflask import launch_server, proxy
from financeager.period import CONFIG_DIR


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_print_rm'
        ,'test_add_get_rm_via_eid'
        ]
    suite.addTest(unittest.TestSuite(map(WebserviceTestCase, tests)))
    return suite

class WebserviceTestCase(unittest.TestCase):
    def setUp(self):
        self.webservice_process = launch_server()
        self.proxy = proxy()
        self.period = "0"
        time.sleep(1)

    def test_add_print_rm(self):
        response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food")
        entry_id = response["id"]

        response = self.proxy.run("print", period=self.period)
        self.assertEqual(response["elements"][0]["name"], "cookies")
        self.assertEqual(len(response["elements"]), 1)

        response = self.proxy.run("rm", period=self.period, name="cookies")
        self.assertEqual(response["id"], entry_id)

        response = self.proxy.run("list")
        self.assertEqual(response["periods"][0], self.period)

    def test_add_get_rm_via_eid(self):
        response = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets")
        eid = response["id"]

        response = self.proxy.run("get", period=self.period, eid=eid)
        self.assertEqual(response["element"]["name"], "donuts")

        response = self.proxy.run("rm", period=self.period, eid=eid)

        response = self.proxy.run("print", period=self.period)
        self.assertEqual(len(response["elements"]), 0)

    def tearDown(self):
        self.proxy.run("stop")
        if self.webservice_process is not None:
            self.webservice_process.kill()
        filepath = os.path.join(CONFIG_DIR, "0.json")
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
