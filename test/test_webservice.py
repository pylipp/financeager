#!/usr/bin/env python

import unittest
import os
import time
from threading import Thread

from financeager.fflask import proxy, launch_server
from financeager.config import CONFIG_DIR
from financeager.model import prettify


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_print_rm',
        'test_add_get_rm_via_eid',
        'test_get_nonexisting_entry',
        'test_delete_nonexisting_entry',
        'test_update',
        'test_recurrent_entry',
        ]
    suite.addTest(unittest.TestSuite(map(WebserviceTestCase, tests)))
    return suite


class WebserviceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        host_ip = "127.0.0.1:5000"
        config = dict(
                debug=False,  # can run reloader only in main thread
                host=host_ip
                )
        cls.flask_thread = Thread(target=launch_server, kwargs=config)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()

        # wait for flask server being launched
        time.sleep(3)

        cls.proxy = proxy()
        cls.period = "1900"  # choosing a value that hopefully does not exist yet
        cls.http_config = {"host": host_ip, "username": None, }

    def test_add_print_rm(self):
        add_response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food", table_name="standard",
                http_config=self.http_config)

        entry_id = add_response["id"]

        response = self.proxy.run("print", period=self.period,
                http_config=self.http_config)
        self.assertGreater(len(prettify(response["elements"])), 0)

        response = self.proxy.run("rm", period=self.period, eid=entry_id,
                http_config=self.http_config)
        self.assertEqual(response["id"], entry_id)

        # FIXME deprecate 'running' arg
        # response = self.proxy.run("list", http_config=self.http_config)
        # self.assertIn(self.period, response["periods"])

    def test_add_get_rm_via_eid(self):
        response = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets", http_config=self.http_config)
        entry_id = response["id"]

        response = self.proxy.run("get", period=self.period, eid=entry_id,
                http_config=self.http_config)
        self.assertEqual(response["element"]["name"], "donuts")

        response = self.proxy.run("rm", period=self.period, eid=entry_id,
                http_config=self.http_config)

        response = self.proxy.run("print", period=self.period,
                http_config=self.http_config)
        self.assertEqual(len(response["elements"]["standard"]), 0)

        self.assertEqual(len(prettify(response["elements"])), 0)

    def test_update(self):
        response = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets", http_config=self.http_config)
        entry_id = response["id"]

        response = self.proxy.run("update", period=self.period, eid=entry_id,
                name="bretzels", http_config=self.http_config)
        self.assertListEqual(list(response.keys()), ["id"])

        response = self.proxy.run("get", period=self.period, eid=entry_id,
                http_config=self.http_config)
        self.assertEqual(response["element"]["name"], "bretzels")

    def test_get_nonexisting_entry(self):
        response = self.proxy.run("get", period=self.period, eid=-1,
                http_config=self.http_config)
        self.assertSetEqual({"error"}, set(response.keys()))

    def test_delete_nonexisting_entry(self):
        response = self.proxy.run("rm", period=self.period, eid=0,
                http_config=self.http_config)
        self.assertSetEqual({"error"}, set(response.keys()))

    def test_invalid_request(self):
        http_config = self.http_config.copy()
        http_config["host"] = "weird.foodomain.nope"
        response = self.proxy.run("get", period=self.period, eid=1,
                http_config=self.http_config)
        self.assertEqual("Element not found.", response["error"])

    def test_recurrent_entry(self):
        add_response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food", table_name="recurrent",
                frequency="half-yearly", start="01-01", end="12-31",
                http_config=self.http_config)
        entry_id = add_response["id"]
        self.assertEqual(entry_id, 1)

        get_response = self.proxy.run("get", period=self.period, eid=entry_id,
                table_name="recurrent", http_config=self.http_config)
        self.assertEqual(get_response["element"]["frequency"], "half-yearly")

        update_response = self.proxy.run("update", period=self.period,
                eid=entry_id, table_name="recurrent",
                frequency="quarter-yearly", name="clifbars",
                http_config=self.http_config)
        self.assertEqual(update_response["id"], entry_id)

        print_response = self.proxy.run("print", period=self.period,
                http_config=self.http_config)
        elements = print_response["elements"]["recurrent"]
        self.assertEqual(len(elements), 1)
        self.assertEqual(len(elements[str(entry_id)]), 4)

        representation = prettify(print_response["elements"])
        self.assertEqual(representation.count("Clifbars"), 4)

        self.proxy.run("rm", period=self.period, eid=entry_id,
                table_name="recurrent", http_config=self.http_config)

        print_response = self.proxy.run("print", period=self.period,
                http_config=self.http_config)
        self.assertEqual(len(print_response["elements"]["recurrent"]), 0)

    def tearDown(self):
        self.proxy.run("stop")
        filepath = os.path.join(CONFIG_DIR, "{}.json".format(self.period))
        if os.path.exists(filepath):
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
