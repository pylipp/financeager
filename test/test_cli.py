#!/usr/bin/env python

import unittest
from unittest import mock
import os
import time
from threading import Thread
import re
import tempfile

from requests import Response, RequestException

from financeager import DEFAULT_TABLE
from financeager.fflask import create_app
from financeager.cli import _parse_command, run, SUCCESS, FAILURE
from financeager.entries import CategoryEntry

TEST_CONFIG_FILEPATH = "/tmp/financeager-test-config"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")


class CliTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test config file for client
        with open(TEST_CONFIG_FILEPATH, "w") as file:
            file.write(cls.CONFIG_FILE_CONTENT)

        cls.period = "1900"  # choosing a year that hopefully does not exist yet
        cls.destination_period = "1901"

        cls.eid_pattern = re.compile(
            r"(Add|Updat|Remov|Copi)ed element (\d+)\.")

    def cli_run(self, command_line, log_method="info", format_args=()):
        """Wrapper around cli.run() function. Adds convenient command line
        options (period and config filepath). Executes the actual run() function
        while patching the module logger info and error methods to catch their
        call arguments.

        'command_line' is a string of the form that financeager is called from
        the command line with. 'format_args' are optional objects that are
        formatted into the command line string. Must be passed as tuple if more
        than one.

        If information about an added/update/removed/copied element was to be
        logged, the corresponding ID is matched from the log call arguments to
        the specified 'log_method' and returned. Otherwise the raw log call is
        returned.
        """
        if not isinstance(format_args, tuple):
            format_args = (format_args,)
        args = command_line.format(*format_args).split()
        command = args[0]

        # Exclude option from subcommand parsers that would be confused
        if command not in ["copy", "list"]:
            args.extend(["--period", self.period])

        args.extend(["--config", TEST_CONFIG_FILEPATH])

        with mock.patch("financeager.cli.logger") as mocked_logger:
            # Mock relevant methods
            mocked_logger.info = mock.MagicMock()
            mocked_logger.error = mock.MagicMock()

            exit_code = run(**_parse_command(args))

            # Record for optional detailed analysis in test methods
            self.log_call_args_list = {}
            for method in ["info", "error"]:
                self.log_call_args_list[method] = \
                    getattr(mocked_logger, method).call_args_list
            # Get first of the args of the first call of specified log method
            printed_content = self.log_call_args_list[log_method][0][0][0]

            # Verify exit code after assigning log_call_args_list member
            self.assertEqual(exit_code,
                             SUCCESS if log_method == "info" else FAILURE)

        if command in ["add", "update", "rm", "copy"] and\
                isinstance(printed_content, str):
            m = re.match(self.eid_pattern, printed_content)
            self.assertIsNotNone(m)
            return int(m.group(2))

        # Convert Exceptions to string
        return str(printed_content)

    def tearDown(self):
        for p in [self.period, self.destination_period]:
            filepath = os.path.join(TEST_DATA_DIR, "{}.json".format(p))
            if os.path.exists(filepath):
                os.remove(filepath)


class CliInvalidConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = """\
[SERVICE]
name = heroku"""

    def test_print(self):
        # using a command that won't try to parse the element ID from the print
        # call in cli_run()...
        printed_content = self.cli_run("print", log_method="error")
        self.assertEqual(printed_content,
                         "Invalid configuration: Unknown service name!")


@mock.patch("financeager.DATA_DIR", None)
class CliLocalServerMemoryStorageTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = ""  # backend 'none' is the default anyway

    @mock.patch("tinydb.storages.MemoryStorage.write")
    def test_add_entry(self, mocked_write):
        entry_id = self.cli_run("add more 1337")
        # Verify that data is written to memory
        self.assertDictContainsSubset({
            "name": "more",
            "value": 1337.0
        }, mocked_write.call_args[0][0]["standard"][entry_id])


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class CliLocalServerTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = """\
[SERVICE]
name = none

[FRONTEND]
default_category = no-category"""

    def test_add_entry(self):
        entry_id = self.cli_run("add entry 42")
        self.assertEqual(entry_id, 1)

        # Verify that customized default category is used
        printed_content = self.cli_run("get {}", format_args=entry_id)
        self.assertEqual(printed_content.splitlines()[-1].split()[1].lower(),
                         "no-category")

    # Interfere call to stderr (see StreamHandler implementation in
    # python3.5/logging/__init__.py)
    @mock.patch("sys.stderr.write")
    def test_verbose(self, mocked_stderr):
        self.cli_run("print --verbose")
        self.assertTrue(mocked_stderr.call_args_list[0][0][0].endswith(
            "Loading custom config from {}".format(TEST_CONFIG_FILEPATH)))

    @mock.patch("financeager.offline.OFFLINE_FILEPATH",
                "/tmp/financeager-test-offline.json")
    def test_offline_feature(self):
        with mock.patch("financeager.server.Server.run") as mocked_run:

            def side_effect(command, **kwargs):
                if command == "print":
                    return {"elements": {DEFAULT_TABLE: {}, "recurrent": {}}}
                elif command == "add":
                    raise TypeError()
                elif command == "stop":
                    return {}
                else:
                    raise NotImplementedError(command)

            # Try do add an item but provoke CommunicationError
            mocked_run.side_effect = side_effect

            try:
                self.cli_run("add veggies -33", log_method="error")
            except AssertionError:
                # The regex matching is expected to fail; hence no return value
                # from cli_run() available
                pass

            # Output from caught CommunicationError
            self.assertEqual("Unexpected error",
                             str(self.log_call_args_list["error"][0][0][0]))
            self.assertEqual("Stored 'add' request in offline backup.",
                             self.log_call_args_list["info"][0][0][0])

            # Now request a print, and try to recover the offline backup
            # But adding is still expected to fail
            self.cli_run("print", log_method="error")
            # Output from print; expect empty database
            self.assertEqual("", self.log_call_args_list["info"][0][0][0])

            # Output from cli module
            self.assertEqual("Offline backup recovery failed!",
                             self.log_call_args_list["error"][-1][0][0])

        # Without side effects, recover the offline backup
        self.cli_run("print")

        self.assertEqual("", self.log_call_args_list["info"][0][0][0])
        self.assertEqual("Recovered offline backup.",
                         self.log_call_args_list["info"][1][0][0])

    def test_get_nonexisting_entry(self):
        printed_content = self.cli_run("get 0", log_method="error")
        self.assertEqual(printed_content, "Invalid request: Element not found.")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class CliFlaskTestCase(CliTestCase):

    HOST_IP = "127.0.0.1:5000"
    CONFIG_FILE_CONTENT = """\
[SERVICE]
name = flask

[FRONTEND]
default_category = unspecified
date_format = %%m-%%d

[SERVICE:FLASK]
host = http://{}
""".format(HOST_IP)

    @staticmethod
    def launch_server():
        # Patch DATA_DIR inside the thread to avoid having it
        # created/interfering with logs on actual machine
        import financeager
        financeager.DATA_DIR = TEST_DATA_DIR
        app = create_app(
            data_dir=TEST_DATA_DIR,
            config={
                "DEBUG": False,  # reloader can only be run in main thread
                "SERVER_NAME": CliFlaskTestCase.HOST_IP,
            })
        app.run()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.flask_thread = Thread(target=cls.launch_server)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()

        # wait for flask server being launched
        time.sleep(3)

    def test_add_print_rm(self):
        entry_id = self.cli_run("add cookies -100")

        printed_content = self.cli_run("print")
        self.assertIn(CategoryEntry.DEFAULT_NAME, printed_content.lower())

        rm_entry_id = self.cli_run("rm {}", format_args=entry_id)
        self.assertEqual(rm_entry_id, entry_id)

        printed_content = self.cli_run("list")
        self.assertIn(self.period, printed_content)

    def test_add_get_rm_via_eid(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        printed_content = self.cli_run("get {}", format_args=entry_id)
        name = printed_content.split("\n")[0].split()[2]
        self.assertEqual(name, "Donuts")

        self.cli_run("rm {}", format_args=entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content, "")

    def test_add_invalid_entry_table_name(self):
        printed_content = self.cli_run(
            "add stuff 11.11 -t unknown", log_method="error")
        self.assertIn("400", printed_content)

    def test_update(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        update_entry_id = self.cli_run(
            "update {} -n bretzels", format_args=entry_id)
        self.assertEqual(entry_id, update_entry_id)

        printed_content = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("Bretzels", printed_content)

        # Remove to have empty period
        self.cli_run("rm {}", format_args=entry_id)

    def test_update_nonexisting_entry(self):
        printed_content = self.cli_run("update -1 -n a", log_method="error")
        self.assertIn("400", printed_content)

    def test_get_nonexisting_entry(self):
        printed_content = self.cli_run("get -1", log_method="error")
        self.assertIn("404", printed_content)

    def test_delete_nonexisting_entry(self):
        printed_content = self.cli_run("rm 0", log_method="error")
        self.assertIn("404", printed_content)

    def test_recurrent_entry(self):
        entry_id = self.cli_run("add cookies -10 -c food -t recurrent -f "
                                "half-yearly -s 01-01 -e 12-31")
        self.assertEqual(entry_id, 1)

        printed_content = self.cli_run(
            "get {} -t recurrent", format_args=entry_id)
        self.assertIn("Half-Yearly", printed_content)

        update_entry_id = self.cli_run(
            "update {} -t recurrent -n clifbars -f quarter-yearly",
            format_args=entry_id)
        self.assertEqual(update_entry_id, entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content.count("Clifbars"), 4)
        self.assertEqual(printed_content.count("{}\n".format(entry_id)), 4)
        self.assertEqual(len(printed_content.splitlines()), 9)

        self.cli_run("rm {} -t recurrent", format_args=entry_id)

        printed_content = self.cli_run("print")
        self.assertEqual(printed_content, "")

    def test_copy(self):
        source_entry_id = self.cli_run("add donuts -50 -c sweets")

        destination_entry_id = self.cli_run(
            "copy {} -s {} -d {}",
            format_args=(source_entry_id, self.period, self.destination_period))

        # Swap period to trick cli_run()
        self.period, self.destination_period = self.destination_period, \
            self.period
        destination_printed_content = self.cli_run(
            "get {}", format_args=destination_entry_id).splitlines()
        self.period, self.destination_period = self.destination_period, \
            self.period

        source_printed_content = self.cli_run(
            "get {}", format_args=source_entry_id).splitlines()
        # Remove date lines
        destination_printed_content.remove(destination_printed_content[2])
        source_printed_content.remove(source_printed_content[2])
        self.assertListEqual(destination_printed_content,
                             source_printed_content)

        self.cli_run("rm {}", format_args=source_entry_id)

    def test_copy_nonexisting_entry(self):
        printed_content = self.cli_run(
            "copy 0 -s {} -d {}",
            log_method="error",
            format_args=(self.period, self.destination_period))
        self.assertIn("404", printed_content)

    def test_default_category(self):
        entry_id = self.cli_run("add car -9999")

        # Default category is converted for frontend display
        printed_content = self.cli_run("print")
        self.assertIn(CategoryEntry.DEFAULT_NAME, printed_content.lower())

        # Category field is converted to 'None' and filtered for
        printed_content = self.cli_run("print --filters category=unspecified")
        self.assertIn(CategoryEntry.DEFAULT_NAME, printed_content.lower())

        # The pattern is used for regex filtering; nothing is found
        printed_content = self.cli_run("print --filters category=lel")
        self.assertEqual(printed_content, "")

        # Default category is converted for frontend display
        printed_content = self.cli_run("get {}", format_args=entry_id)
        self.assertEqual(printed_content.splitlines()[-1].split()[1].lower(),
                         CategoryEntry.DEFAULT_NAME)

        self.cli_run("rm {}", format_args=entry_id)

    def test_communication_error(self):
        with mock.patch("requests.get") as mocked_get:
            response = Response()
            response.status_code = 500
            mocked_get.return_value = response
            printed_content = self.cli_run("print", log_method="error")
            self.assertIn("500", printed_content)

    @mock.patch("financeager.offline.OFFLINE_FILEPATH",
                "/tmp/financeager-test-offline.json")
    def test_offline_feature(self):
        with mock.patch("requests.post") as mocked_post:
            # Try do add an item but provoke CommunicationError
            mocked_post.side_effect = RequestException("did not work")

            try:
                self.cli_run("add veggies -33", log_method="error")
            except AssertionError:
                # The regex matching is expected to fail
                pass

            # Output from caught CommunicationError
            self.assertEqual("Error sending request: did not work",
                             str(self.log_call_args_list["error"][0][0][0]))
            self.assertEqual("Stored 'add' request in offline backup.",
                             self.log_call_args_list["info"][0][0][0])

            # Now request a print, and try to recover the offline backup
            # But adding is still expected to fail
            mocked_post.side_effect = RequestException("still no works")
            self.cli_run("print", log_method="error")
            # Output from print; expect empty database
            self.assertEqual("", self.log_call_args_list["info"][0][0][0])

            # Output from cli module
            self.assertEqual("Offline backup recovery failed!",
                             self.log_call_args_list["error"][-1][0][0])

        # Without side effects, recover the offline backup
        self.cli_run("print")

        self.assertEqual("", self.log_call_args_list["info"][0][0][0])
        # TODO: adjust offline module implementation
        # self.assertEqual("Added element 1.",
        #                  self.log_call_args_list[][1][0][0])
        self.assertEqual("Recovered offline backup.",
                         self.log_call_args_list["info"][1][0][0])

        # This is admittedly hacky. It would be cleaner to a) have independent
        # databases per test function, or b) have a way to get the response
        # about the recovered element ID by having the offline module use
        # functions of the cli module
        self.cli_run("rm 5")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
@mock.patch("financeager.CONFIG_FILEPATH", TEST_CONFIG_FILEPATH)
class CliNoConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = "[FRONTEND]\ndefault_category = wayne"

    @mock.patch("financeager.cli.logger")
    def test_print(self, mocked_logger):
        mocked_logger.info = mock.MagicMock()

        # Default config file exists; expect it to be loaded
        run(command="print", period=self.period, config=None)
        mocked_logger.info.assert_called_once_with("")
        mocked_logger.info.reset_mock()

        # Remove default config file
        os.remove(TEST_CONFIG_FILEPATH)

        # No config is loaded at all
        run(command="print", period=1900, config=None)
        mocked_logger.info.assert_called_once_with("")

        # The custom config modified the global state which affects other
        # tests...
        CategoryEntry.DEFAULT_NAME = "unspecified"


if __name__ == "__main__":
    unittest.main()
