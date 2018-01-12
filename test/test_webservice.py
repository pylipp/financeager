#!/usr/bin/env python

import unittest
import os
import time
from threading import Thread

from financeager.fflask import launch_server
from financeager.httprequests import proxy
from financeager import CONFIG_DIR
from financeager.model import prettify


# Periods are stored to disk. The CONFIG_DIR is expected to exist
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_print_rm',
        'test_add_get_rm_via_eid',
        'test_get_nonexisting_entry',
        'test_delete_nonexisting_entry',
        'test_update',
        'test_copy',
        'test_recurrent_entry',
        'test_parser_error'
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

        cls.proxy = proxy(http_config={"host": host_ip, "username": None})
        cls.period = "1900"  # choosing a value that hopefully does not exist yet
        cls.destination_period = "1901"

    def test_add_print_rm(self):
        add_response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food", table_name="standard")

        entry_id = add_response["id"]

        response = self.proxy.run("print", period=self.period)
        self.assertGreater(len(prettify(response["elements"])), 0)

        response = self.proxy.run("rm", period=self.period, eid=entry_id)
        self.assertEqual(response["id"], entry_id)

        response = self.proxy.run("list")
        self.assertIn(self.period, response["periods"])

    def test_add_get_rm_via_eid(self):
        response = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets")
        entry_id = response["id"]

        response = self.proxy.run("get", period=self.period, eid=entry_id)
        self.assertEqual(response["element"]["name"], "donuts")

        response = self.proxy.run("rm", period=self.period, eid=entry_id)

        response = self.proxy.run("print", period=self.period)
        self.assertEqual(len(response["elements"]["standard"]), 0)

        self.assertEqual(len(prettify(response["elements"])), 0)

    def test_update(self):
        response = self.proxy.run("add", period=self.period, name="donuts",
                value="-50", category="sweets")
        entry_id = response["id"]

        response = self.proxy.run("update", period=self.period, eid=entry_id,
                name="bretzels")
        self.assertListEqual(list(response.keys()), ["id"])

        response = self.proxy.run("get", period=self.period, eid=entry_id)
        self.assertEqual(response["element"]["name"], "bretzels")

    def test_get_nonexisting_entry(self):
        response = self.proxy.run("get", period=self.period, eid=-1)
        self.assertSetEqual({"error"}, set(response.keys()))

    def test_delete_nonexisting_entry(self):
        response = self.proxy.run("rm", period=self.period, eid=0)
        self.assertSetEqual({"error"}, set(response.keys()))

    def test_invalid_request(self):
        # insert invalid host, reset to original in the end
        original_host = self.proxy.http_config["host"]
        self.proxy.http_config["host"] = "weird.foodomain.nope"

        response = self.proxy.run("get", period=self.period, eid=1)
        self.assertEqual("Element not found.", response["error"])

        self.proxy.http_config["host"] = original_host

    def test_recurrent_entry(self):
        add_response = self.proxy.run("add", period=self.period, name="cookies",
                value="-100", category="food", table_name="recurrent",
                frequency="half-yearly", start="01-01", end="12-31")
        entry_id = add_response["id"]
        self.assertEqual(entry_id, 1)

        get_response = self.proxy.run("get", period=self.period, eid=entry_id,
                table_name="recurrent")
        self.assertEqual(get_response["element"]["frequency"], "half-yearly")

        update_response = self.proxy.run("update", period=self.period,
                eid=entry_id, table_name="recurrent",
                frequency="quarter-yearly", name="clifbars")
        self.assertEqual(update_response["id"], entry_id)

        print_response = self.proxy.run("print", period=self.period)
        elements = print_response["elements"]["recurrent"]
        self.assertEqual(len(elements), 1)
        self.assertEqual(len(elements[str(entry_id)]), 4)

        representation = prettify(print_response["elements"])
        self.assertEqual(representation.count("Clifbars"), 4)

        self.proxy.run("rm", period=self.period, eid=entry_id,
                table_name="recurrent")

        print_response = self.proxy.run("print", period=self.period)
        self.assertEqual(len(print_response["elements"]["recurrent"]), 0)

    def tearDown(self):
        self.proxy.run("stop")
        for p in [self.period, self.destination_period]:
            filepath = os.path.join(CONFIG_DIR, "{}.json".format(p))
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_copy(self):
        fields = dict(name="donuts", value=-50.0, category="sweets")
        response = self.proxy.run("add", period=self.period, **fields)
        source_entry_id = response["id"]

        response = self.proxy.run(
            "copy", source_period=self.period,
            destination_period=self.destination_period,
            eid=source_entry_id)
        destination_entry_id = response["id"]

        get_response = self.proxy.run(
            "get", period=self.destination_period, eid=destination_entry_id)
        self.assertTrue(set(fields.items()).issubset(
            set(get_response["element"].items())))

    def test_parser_error(self):
        # missing name and value in request, parser will complain
        response = self.proxy.run("add", period=self.period)
        self.assertIn("name", response["error"])


if __name__ == "__main__":
    unittest.main()
