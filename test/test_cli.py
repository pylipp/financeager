#!/usr/bin/env python

import unittest
from unittest import mock
import os
import time
from threading import Thread
import re

from requests import Response

from financeager.fflask import launch_server
from financeager.httprequests import InvalidRequest
from financeager import CONFIG_DIR
from financeager.cli import _parse_command, run


# Periods are stored to disk. The CONFIG_DIR is expected to exist
if not os.path.isdir(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_add_print_rm',
        'test_add_get_rm_via_eid',
        # 'test_add_invalid_entry',
        'test_add_invalid_entry_table_name',
        'test_get_nonexisting_entry',
        'test_delete_nonexisting_entry',
        'test_update',
        'test_update_nonexisting_entry',
        'test_copy',
        'test_copy_nonexisting_entry',
        'test_recurrent_entry',
        # 'test_parser_error',
        'test_communication_error',
        ]
    suite.addTest(unittest.TestSuite(map(CliTestCase, tests)))
    return suite


class CliTestCase(unittest.TestCase):

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

        # Create test config file for client
        cls.config_filepath = "/tmp/financeager-test-config"
        with open(cls.config_filepath, "w") as file:
            file.write("""\
[SERVICE]
name = flask

[FRONTEND]
default_category = unspecified
date_format = %%m-%%d

[SERVICE:FLASK]
host = {}
""".format(host_ip)
                       )
        cls.period = "1900"  # choosing a value that hopefully does not exist yet
        cls.destination_period = "1901"

        cls.eid_pattern = re.compile(r"(Add|Updat|Remov|Copi)ed element (\d+)\.")

    def cli_run(self, command_line, *format_args):
        """Wrapper around cli.run() function. Adds convenient command line
        options (period and config filepath). Executes the actual run() function
        while patching the built-in print() to catch its call arguments.

        'command_line' is a string of the form that financeager is called from
        the command line with. 'format_args' are optional objects that are
        formatted into the command line string.

        If information about an added/update/removed/copied element was to be
        printed, the corresponding ID is matched from the print call arguments
        and returned. Otherwise the raw print call is returned.
        """
        args = command_line.format(*format_args).split()
        command = args[0]

        # Exclude option from subcommand parsers that would be confused
        if command not in ["copy", "list"]:
            args.extend(["--period", self.period])

        args.extend(["--config", self.config_filepath])

        with mock.patch("builtins.print") as mocked_print:
            run(**_parse_command(args))
            # Get first of the args
            printed_content = mocked_print.call_args[0][0]

        if command in ["add", "update", "rm", "copy"] and\
                isinstance(printed_content, str):
            m = re.match(self.eid_pattern, printed_content)
            self.assertIsNotNone(m)
            return int(m.group(2))

        # Convert Exceptions to string
        return str(printed_content)

    def test_add_print_rm(self):
        entry_id = self.cli_run("add cookies -100 -c food")

        printed_content = self.cli_run("print")
        self.assertGreater(len(printed_content), 0)

        rm_entry_id = self.cli_run("rm {}", entry_id)
        self.assertEqual(rm_entry_id, entry_id)

        printed_content = self.cli_run("list")
        self.assertIn(self.period, printed_content)

    def test_add_get_rm_via_eid(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        printed_content = self.cli_run("get {}", entry_id)
        name = printed_content.split("\n")[0].split()[2]
        self.assertEqual(name, "Donuts")

        self.cli_run("rm {}", entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content, "")

    def test_add_invalid_entry(self):
        with self.assertRaises(InvalidRequest) as cm:
            self.proxy.run("add", period=self.period, name="")
        self.assertIn("400", cm.exception.args[0])

    def test_add_invalid_entry_table_name(self):
        printed_content = self.cli_run("add stuff 11.11 -t unknown")
        self.assertIn("400", printed_content)

    def test_update(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        update_entry_id = self.cli_run("update {} -n bretzels", entry_id)
        self.assertEqual(entry_id, update_entry_id)

        printed_content = self.cli_run("get {}", entry_id)
        self.assertIn("Bretzels", printed_content)

        # Remove to have empty period
        self.cli_run("rm {}", entry_id)

    def test_update_nonexisting_entry(self):
        printed_content = self.cli_run("update -1 -n a")
        self.assertIn("400", printed_content)

    def test_get_nonexisting_entry(self):
        printed_content = self.cli_run("get -1")
        self.assertIn("404", printed_content)

    def test_delete_nonexisting_entry(self):
        printed_content = self.cli_run("rm 0")
        self.assertIn("404", printed_content)

    def test_invalid_request(self):
        # insert invalid host, reset to original in the end
        original_host = self.proxy.http_config["host"]
        self.proxy.http_config["host"] = "weird.foodomain.nope"

        response = self.proxy.run("get", period=self.period, eid=1)
        self.assertEqual("Element not found.", response["error"])

        self.proxy.http_config["host"] = original_host

    def test_recurrent_entry(self):
        entry_id = self.cli_run("add cookies -10 -c food -t recurrent -f "
                                "half-yearly -s 01-01 -e 12-31")
        self.assertEqual(entry_id, 1)

        printed_content = self.cli_run("get {} -t recurrent", entry_id)
        self.assertIn("Half-yearly", printed_content)

        update_entry_id = self.cli_run("update {} -t recurrent -n clifbars "
                                       "-f quarter-yearly", entry_id)
        self.assertEqual(update_entry_id, entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content.count("Clifbars"), 4)
        self.assertEqual(printed_content.count("{}\n".format(entry_id)), 4)
        self.assertEqual(len(printed_content.splitlines()), 9)

        self.cli_run("rm {} -t recurrent", entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content, "")

    def tearDown(self):
        for p in [self.period, self.destination_period]:
            filepath = os.path.join(CONFIG_DIR, "{}.json".format(p))
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_copy(self):
        source_entry_id = self.cli_run("add donuts -50 -c sweets")

        destination_entry_id = self.cli_run(
            "copy {} -s {} -d {}", source_entry_id, self.period,
            self.destination_period)

        # Swap period to trick cli_run()
        self.period, self.destination_period = self.destination_period, self.period
        destination_printed_content = self.cli_run(
            "get {}", destination_entry_id).splitlines()
        self.period, self.destination_period = self.destination_period, self.period

        source_printed_content = self.cli_run("get {}",
                                              source_entry_id).splitlines()
        # Remove date lines
        destination_printed_content.remove(destination_printed_content[2])
        source_printed_content.remove(source_printed_content[2])
        self.assertListEqual(destination_printed_content,
                             source_printed_content)

        self.cli_run("rm {}", source_entry_id)

    def test_copy_nonexisting_entry(self):
        printed_content = self.cli_run("copy 0 -s {} -d {}", self.period,
                                       self.destination_period)
        self.assertIn("404", printed_content)

    def test_parser_error(self):
        # missing name and value in request, parser will complain
        with self.assertRaises(InvalidRequest) as cm:
            self.proxy.run("add", period=self.period)
        self.assertIn("400", cm.exception.args[0])

    def test_communication_error(self):
        with mock.patch("requests.get") as mocked_get:
            response = Response()
            response.status_code = 500
            mocked_get.return_value = response
            printed_content = self.cli_run("print")
            self.assertIn("500", printed_content)


if __name__ == "__main__":
    unittest.main()
