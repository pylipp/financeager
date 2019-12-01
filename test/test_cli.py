import unittest
from unittest import mock
import os
import time
from threading import Thread
import tempfile
from collections import defaultdict

from requests import Response, RequestException
from requests import get as requests_get

from financeager import DEFAULT_TABLE, config
from financeager.communication import Client
from financeager.fflask import create_app
from financeager.cli import _parse_command, run, SUCCESS, FAILURE, _preprocess,\
    _format_response
from financeager.entries import CategoryEntry
from financeager.exceptions import PreprocessingError

TEST_CONFIG_FILEPATH = "/tmp/financeager-test-config"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")


class CliTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test config file for client
        with open(TEST_CONFIG_FILEPATH, "w") as file:
            file.write(cls.CONFIG_FILE_CONTENT)

        try:
            cls.configuration = config.Configuration(
                filepath=TEST_CONFIG_FILEPATH)
        except config.InvalidConfigError:
            cls.configuration = None

        cls.period = 1900

    def setUp(self):
        # Separate test runs by running individual test methods using distinct
        # periods (especially crucial for CliFlaskTestCase which uses a single
        # Flask instance for all tests)
        self.__class__.period += 1

        # Mocks to record output of cli.run() call
        self.info = mock.MagicMock()
        self.error = mock.MagicMock()

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
        self.info.reset_mock()
        self.error.reset_mock()

        if not isinstance(format_args, tuple):
            format_args = (format_args,)
        args = command_line.format(*format_args).split()
        command = args[0]

        # Exclude option from subcommand parsers that would be confused
        if command not in ["copy", "periods"]:
            args.extend(["--period", str(self.period)])

        args.extend(["--config-filepath", TEST_CONFIG_FILEPATH])

        sinks = Client.Sinks(self.info, self.error)

        params = _parse_command(args)
        exit_code = run(sinks=sinks, **params)

        # Get first of the args of the call of specified log method
        response = getattr(self, log_method).call_args[0][0]

        # Verify exit code
        self.assertEqual(exit_code,
                         SUCCESS if log_method == "info" else FAILURE)

        # Immediately return str messages
        if isinstance(response, str):
            return response

        # Convert Exceptions to string
        if isinstance(response, Exception):
            return str(response)

        if command in ["add", "update", "remove", "copy"]:
            return response["id"]

        if command in ["get", "list", "periods"] and log_method == "info":
            return _format_response(
                response,
                command,
                default_category=self.configuration.get_option(
                    "FRONTEND", "default_category"))

        return response


class CliInvalidConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = """\
[SERVICE]
name = heroku"""

    def test_list(self):
        # using a command that won't try to parse the element ID from the list
        # call in cli_run()...
        response = self.cli_run("list", log_method="error")
        self.assertEqual(response,
                         "Invalid configuration: Unknown service name!")


@mock.patch("financeager.DATA_DIR", None)
class CliLocalServerMemoryStorageTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = ""  # service 'none' is the default anyway

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
        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("no-category", response.lower())

    # Interfere call to stderr (see StreamHandler implementation in
    # python3.5/logging/__init__.py)
    @mock.patch("sys.stderr.write")
    def test_verbose(self, mocked_stderr):
        self.cli_run("list --verbose")
        self.assertIn(
            "Loading custom config from {}".format(TEST_CONFIG_FILEPATH),
            mocked_stderr.call_args_list[0][0][0])

    @mock.patch("financeager.offline.OFFLINE_FILEPATH",
                "/tmp/financeager-test-offline.json")
    def test_offline_feature(self):
        with mock.patch("financeager.server.Server.run") as mocked_run:

            def side_effect(command, **kwargs):
                if command == "list":
                    return {"elements": {DEFAULT_TABLE: {}, "recurrent": {}}}
                elif command == "add":
                    raise TypeError()
                elif command == "stop":
                    return {}
                else:
                    raise NotImplementedError(command)

            # Try do add an item but provoke CommunicationError
            mocked_run.side_effect = side_effect

            self.cli_run("add veggies -33", log_method="error")

            # Output from caught CommunicationError
            self.assertEqual("Unexpected error",
                             str(self.error.call_args_list[0][0][0]))
            self.assertEqual("Stored 'add' request in offline backup.",
                             self.info.call_args_list[0][0][0])

            # Now request a print, and try to recover the offline backup
            # But adding is still expected to fail
            response = self.cli_run("list", log_method="error")
            # Output from print; expect empty database
            self.assertEqual({"elements": {
                DEFAULT_TABLE: {},
                "recurrent": {}
            }}, self.info.call_args_list[0][0][0])

            # Output from cli module
            self.assertEqual("Offline backup recovery failed!", response)

        # Without side effects, recover the offline backup
        self.cli_run("list")

        # Output from list command
        self.assertEqual(
            self.info.call_args_list[0][0][0],
            {'elements': {
                'standard': {},
                'recurrent': defaultdict(list)
            }})
        # Output from recovered add command
        self.assertEqual({"id": 1}, self.info.call_args_list[1][0][0])
        self.assertEqual("Recovered offline backup.",
                         self.info.call_args_list[2][0][0])

    def test_get_nonexisting_entry(self):
        response = self.cli_run("get 0", log_method="error")
        self.assertEqual(response, "Invalid request: Element not found.")

    def test_preprocessing_error(self):
        response = self.cli_run("add car -1000 -d ups", log_method="error")
        self.assertEqual(response, "Invalid date format.")


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

        def shutdown():
            from flask import request
            app._server.run('stop')
            request.environ.get("werkzeug.server.shutdown")()
            return ""

        # For testing, add rule to shutdown Flask app
        app.add_url_rule("/stop", "stop", shutdown)

        app.run()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.flask_thread = Thread(target=cls.launch_server)
        cls.flask_thread.start()

        # wait for flask server being launched
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        # Invoke shutting down of Flask app
        requests_get("http://{}/stop".format(cls.HOST_IP))

    def test_add_list_remove(self):
        entry_id = self.cli_run("add cookies -100")

        response = self.cli_run("list")
        self.assertIn(CategoryEntry.DEFAULT_NAME, response.lower())

        remove_entry_id = self.cli_run("remove {}", format_args=entry_id)
        self.assertEqual(remove_entry_id, entry_id)

        response = self.cli_run("periods")
        self.assertIn(str(self.period), response)

    def test_add_get_remove_via_eid(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        response = self.cli_run("get {}", format_args=entry_id)
        name = response.split("\n")[0].split()[2]
        self.assertEqual(name, "Donuts")

        self.cli_run("remove {}", format_args=entry_id)

        response = self.cli_run("list")
        self.assertEqual(response, "")

    def test_add_invalid_entry_table_name(self):
        response = self.cli_run(
            "add stuff 11.11 -t unknown", log_method="error")
        self.assertIn("400", response)

    def test_update(self):
        entry_id = self.cli_run("add donuts -50 -c sweets")

        update_entry_id = self.cli_run(
            "update {} -n bretzels", format_args=entry_id)
        self.assertEqual(entry_id, update_entry_id)

        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("Bretzels", response)

    def test_update_nonexisting_entry(self):
        response = self.cli_run("update -1 -n a", log_method="error")
        self.assertIn("400", response)

    def test_get_nonexisting_entry(self):
        response = self.cli_run("get -1", log_method="error")
        self.assertIn("404", response)

    def test_remove_nonexisting_entry(self):
        response = self.cli_run("remove 0", log_method="error")
        self.assertIn("404", response)

    def test_recurrent_entry(self):
        entry_id = self.cli_run("add cookies -10 -c food -t recurrent -f "
                                "half-yearly -s 01-01 -e 12-31")
        self.assertEqual(entry_id, 1)

        response = self.cli_run("get {} -t recurrent", format_args=entry_id)
        self.assertIn("Half-Yearly", response)

        update_entry_id = self.cli_run(
            "update {} -t recurrent -n clifbars -f quarter-yearly",
            format_args=entry_id)
        self.assertEqual(update_entry_id, entry_id)

        response = self.cli_run("list")
        self.assertEqual(response.count("Clifbars"), 4)
        self.assertEqual(response.count("{}\n".format(entry_id)), 4)
        self.assertEqual(len(response.splitlines()), 9)

        self.cli_run("remove {} -t recurrent", format_args=entry_id)

        response = self.cli_run("list")
        self.assertEqual(response, "")

    def test_copy(self):
        destination_period = self.period + 1
        self.__class__.period += 1

        source_entry_id = self.cli_run("add donuts -50 -c sweets")

        destination_entry_id = self.cli_run(
            "copy {} -s {} -d {}",
            format_args=(source_entry_id, self.period, destination_period))

        # Swap period to trick cli_run()
        self.period, destination_period = destination_period, self.period
        destination_printed_content = self.cli_run(
            "get {}", format_args=destination_entry_id).splitlines()
        self.period, destination_period = destination_period, self.period

        source_printed_content = self.cli_run(
            "get {}", format_args=source_entry_id).splitlines()
        # Remove date lines
        destination_printed_content.remove(destination_printed_content[2])
        source_printed_content.remove(source_printed_content[2])
        self.assertListEqual(destination_printed_content,
                             source_printed_content)

    def test_copy_nonexisting_entry(self):
        destination_period = self.period + 1
        self.__class__.period += 1

        response = self.cli_run(
            "copy 0 -s {} -d {}",
            log_method="error",
            format_args=(self.period, destination_period))
        self.assertIn("404", response)

    def test_default_category(self):
        entry_id = self.cli_run("add car -9999")

        # Default category is converted for frontend display
        response = self.cli_run("list")
        self.assertIn(CategoryEntry.DEFAULT_NAME, response.lower())

        # Category field is converted to 'None' and filtered for
        response = self.cli_run("list --filters category=unspecified")
        self.assertIn(CategoryEntry.DEFAULT_NAME, response.lower())

        # The pattern is used for regex filtering; nothing is found
        response = self.cli_run("list --filters category=lel")
        self.assertEqual(response, "")

        # Default category is converted for frontend display
        response = self.cli_run("get {}", format_args=entry_id)
        self.assertEqual(response.splitlines()[-1].split()[1].lower(),
                         CategoryEntry.DEFAULT_NAME)

    def test_communication_error(self):
        with mock.patch("requests.get") as mocked_get:
            response = Response()
            response.status_code = 500
            mocked_get.return_value = response
            response = self.cli_run("list", log_method="error")
            self.assertIn("500", response)

    @mock.patch("financeager.offline.OFFLINE_FILEPATH",
                "/tmp/financeager-test-offline.json")
    def test_offline_feature(self):
        with mock.patch("requests.post") as mocked_post:
            # Try do add an item but provoke CommunicationError
            mocked_post.side_effect = RequestException("did not work")

            self.cli_run("add veggies -33", log_method="error")

            # Output from caught CommunicationError
            self.assertEqual("Error sending request: did not work",
                             str(self.error.call_args_list[0][0][0]))
            self.assertEqual("Stored 'add' request in offline backup.",
                             self.info.call_args_list[0][0][0])

            # Now request a print, and try to recover the offline backup
            # But adding is still expected to fail
            mocked_post.side_effect = RequestException("still no works")
            self.cli_run("list", log_method="error")
            # Output from print; expect empty database
            self.assertEqual({"elements": {
                DEFAULT_TABLE: {},
                "recurrent": {}
            }}, self.info.call_args_list[0][0][0])

            # Output from cli module
            self.assertEqual("Offline backup recovery failed!",
                             self.error.call_args_list[-1][0][0])

        # Without side effects, recover the offline backup
        self.cli_run("list")

        # Output from list command
        self.assertEqual({"elements": {
            DEFAULT_TABLE: {},
            "recurrent": {}
        }}, self.info.call_args_list[0][0][0])
        # Output from recovered add command
        self.assertEqual({"id": 1}, self.info.call_args_list[1][0][0])
        self.assertEqual("Recovered offline backup.",
                         self.info.call_args_list[2][0][0])


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
@mock.patch("financeager.CONFIG_FILEPATH", TEST_CONFIG_FILEPATH)
class CliNoConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = "[FRONTEND]\ndefault_category = wayne"

    @mock.patch("financeager.cli.logger")
    def test_print_periods(self, mocked_logger):
        mocked_logger.info = mock.MagicMock()
        formatting_options = dict(
            stacked_layout=False, entry_sort="name", category_sort="value")

        # Default config file exists; expect it to be loaded
        run(command="periods", config=None, **formatting_options)
        mocked_logger.info.assert_called_once_with("")
        mocked_logger.info.reset_mock()

        # Remove default config file
        os.remove(TEST_CONFIG_FILEPATH)

        # No config is loaded at all
        run(command="periods", config=None, **formatting_options)
        mocked_logger.info.assert_called_once_with("")

        # The custom config modified the global state which affects other
        # tests...
        CategoryEntry.DEFAULT_NAME = "unspecified"


class PreprocessTestCase(unittest.TestCase):
    def test_date_format(self):
        data = {"date": "31.01."}
        _preprocess(data, date_format="%d.%m.")
        self.assertDictEqual(data, {"date": "01-31"})

    def test_date_format_error(self):
        data = {"date": "01-01"}
        self.assertRaises(
            PreprocessingError, _preprocess, data, date_format="%d.%m")

    def test_name_filters(self):
        data = {"filters": ["name=italian"]}
        _preprocess(data)
        self.assertEqual(data["filters"], {"name": "italian"})

    def test_category_filters(self):
        data = {"filters": ["category=Restaurants"]}
        _preprocess(data)
        self.assertEqual(data["filters"], {"category": "restaurants"})

    def test_filters_error(self):
        data = {"filters": ["value-123"]}
        self.assertRaises(PreprocessingError, _preprocess, data)

    def test_default_category_filter(self):
        data = {"filters": ["category=unspecified"]}
        _preprocess(data)
        self.assertEqual(data["filters"], {"category": None})


class FormatResponseTestCase(unittest.TestCase):
    def test_add(self):
        self.assertEqual("Added element 1.", _format_response({"id": 1}, "add"))

    def test_update(self):
        self.assertEqual("Updated element 1.",
                         _format_response({"id": 1}, "update"))

    def test_remove(self):
        self.assertEqual("Removed element 1.",
                         _format_response({"id": 1}, "remove"))

    def test_copy(self):
        self.assertEqual("Copied element 1.", _format_response({"id": 1},
                                                               "copy"))


if __name__ == "__main__":
    unittest.main()
