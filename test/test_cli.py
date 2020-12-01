import os
import tempfile
import unittest
from datetime import datetime as dt
from unittest import mock

from financeager import (cli, clients, config, exceptions,
                         setup_log_file_handler)

TEST_CONFIG_FILEPATH = "/tmp/financeager-test-config"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")
setup_log_file_handler(TEST_DATA_DIR)


class CliTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test config file for client
        with open(TEST_CONFIG_FILEPATH, "w") as file:
            file.write(cls.CONFIG_FILE_CONTENT)

        cls.period = 1900

    def setUp(self):
        # Separate test runs by running individual test methods using distinct
        # periods (especially crucial for CliFlaskTestCase which uses a single
        # Flask instance for all tests)
        self.__class__.period += 1

        # Mocks to record output of cli.run() call
        self.info = mock.MagicMock()
        self.error = mock.MagicMock()

    def tearDown(self):
        database_filepath = os.path.join(
            TEST_DATA_DIR, "{}.json".format(self.__class__.period))
        # Not all test cases produce database files
        if os.path.exists(database_filepath):
            os.remove(database_filepath)

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

        sinks = clients.Client.Sinks(self.info, self.error)

        # Procedure similar to cli.main()
        params = cli._parse_command(args)
        configuration = config.Configuration(params.pop("config_filepath"))
        exit_code = cli.run(sinks=sinks, configuration=configuration, **params)

        # Get first of the args of the call of specified log method
        response = getattr(self, log_method).call_args[0][0]

        # Verify exit code
        self.assertEqual(exit_code,
                         cli.SUCCESS if log_method == "info" else cli.FAILURE)

        # Immediately return str messages
        if isinstance(response, str):
            return response

        # Convert Exceptions to string
        if isinstance(response, Exception):
            return str(response)

        if command in ["add", "update", "remove", "copy"]:
            return response["id"]

        if command in ["get", "list", "periods"] and log_method == "info":
            return cli._format_response(
                response,
                command,
                default_category=configuration.get_option(
                    "FRONTEND", "default_category"))

        return response


@mock.patch("financeager.DATA_DIR", None)
class CliLocalServerNoneConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = ""  # service 'none' is the default anyway

    @mock.patch("tinydb.storages.MemoryStorage.write")
    def test_add_entry(self, mocked_write):
        entry_id = self.cli_run("add more 1337")
        # Verify that data is written to memory
        self.assertDictContainsSubset({
            "name": "more",
            "value": 1337.0
        }, mocked_write.call_args[0][0]["standard"][entry_id])

    @mock.patch("builtins.print")
    @mock.patch("financeager.cli.logger.info")
    def test_periods(self, mocked_info, mocked_print):
        cli.run(
            "periods",
            configuration=config.Configuration(filepath=TEST_CONFIG_FILEPATH))

        mocked_info.assert_called_once_with({"periods": []})
        mocked_print.assert_called_once_with("")

    @mock.patch("builtins.print")
    @mock.patch("financeager.localserver.Proxy.run")
    def test_str_response(self, mocked_run, mocked_print):
        # Cover the behavior of cli._format_response() given a str
        mocked_run.return_value = "response"
        cli.run(
            "periods",
            configuration=config.Configuration(filepath=TEST_CONFIG_FILEPATH))

        self.assertListEqual(
            mocked_run.mock_calls,
            [mock.call("periods"), mock.call("stop")])
        mocked_print.assert_called_once_with("response")


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

    def test_get_nonexisting_entry(self):
        response = self.cli_run("get 0", log_method="error")
        self.assertEqual(response, "Invalid request: Element not found.")

    def test_preprocessing_error(self):
        response = self.cli_run("add car -1000 -d ups", log_method="error")
        self.assertEqual(response, "Invalid date format.")

    def test_verbose(self):
        entry_id = self.cli_run("add stuff 100 --verbose")
        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("stuff", response.lower())

    def test_list_month(self):
        month_nr = 1
        month_variants = ["01", "Jan", "January"]
        current_month = dt.today().month
        if current_month == month_nr:
            month_nr = 2
            month_variants = ["02", "Feb", "February"]
        month_variants.append(month_nr)

        self.cli_run("add beans -4 -d 0{}-01", format_args=month_nr)
        self.cli_run("add chili -4 -d 0{}-01", format_args=month_nr + 1)

        for m in month_variants:
            response = self.cli_run("list --month {}", format_args=m).lower()
            self.assertIn("beans", response)
            self.assertNotIn("chili", response)

        # Verify overwriting of 'filters' option
        response = self.cli_run(
            "list --month {} --filters date=0{}-",
            format_args=(month_nr, month_nr + 1)).lower()
        self.assertIn("beans", response)
        self.assertNotIn("chili", response)

        # Verify default behavior
        response = self.cli_run("list --month").lower()

        # If it's January: beans -> Feb, chili -> Mar ==> no match
        # Otherwise:       beans -> Jan, chili -> Feb ==> match only in Feb
        if current_month == month_nr + 1:
            self.assertNotIn("beans", response)
            self.assertIn("chili", response)
        else:
            self.assertNotIn("beans", response)
            self.assertNotIn("chili", response)

    def test_list_invalid_month(self):
        month_nr = 13
        response = self.cli_run(
            "list -m {}", format_args=month_nr, log_method="error")
        self.assertEqual(response, "Invalid month: {}".format(month_nr))

    def test_list_filter_value(self):
        self.cli_run("add money 10")
        response = self.cli_run("list -f value=10").lower()
        self.assertIn("money", response)
        self.assertIn("10.00", response)

    @mock.patch("financeager.server.Server.run")
    def test_communication_error(self, mocked_run):
        # Raise exception on first call, behave fine on stop call
        mocked_run.side_effect = [Exception(), {}]
        response = self.cli_run("list", log_method="error")
        self.assertEqual(response, "Unexpected error")

    @mock.patch("financeager.localserver.Proxy.run")
    def test_unexpected_error(self, mocked_run):
        # Raise exception on first call, behave fine on stop call
        mocked_run.side_effect = [Exception(), {}]
        response = self.cli_run("list", log_method="error")
        self.assertTrue(response.startswith("Unexpected error: Traceback"))


class PreprocessTestCase(unittest.TestCase):
    def test_date_format(self):
        data = {"date": "31.01."}
        cli._preprocess(data, date_format="%d.%m.")
        self.assertDictEqual(data, {"date": "01-31"})

    def test_leap_year_date(self):
        data = {"date": "29.02."}
        cli._preprocess(data, date_format="%d.%m.")
        self.assertDictEqual(data, {"date": "02-29"})

    def test_date_format_error(self):
        data = {"date": "01-01"}
        self.assertRaises(
            exceptions.PreprocessingError,
            cli._preprocess,
            data,
            date_format="%d.%m")

    def test_name_filters(self):
        data = {"filters": ["name=italian"]}
        cli._preprocess(data)
        self.assertEqual(data["filters"], {"name": "italian"})

    def test_category_filters(self):
        data = {"filters": ["category=Restaurants"]}
        cli._preprocess(data)
        self.assertEqual(data["filters"], {"category": "restaurants"})

    def test_filters_error(self):
        data = {"filters": ["value-123"]}
        self.assertRaises(exceptions.PreprocessingError, cli._preprocess, data)

    def test_default_category_filter(self):
        data = {"filters": ["category=unspecified"]}
        cli._preprocess(data)
        self.assertEqual(data["filters"], {"category": None})


class FormatResponseTestCase(unittest.TestCase):
    def test_add(self):
        self.assertEqual("Added element 1.",
                         cli._format_response({"id": 1}, "add"))

    def test_update(self):
        self.assertEqual("Updated element 1.",
                         cli._format_response({"id": 1}, "update"))

    def test_remove(self):
        self.assertEqual("Removed element 1.",
                         cli._format_response({"id": 1}, "remove"))

    def test_copy(self):
        self.assertEqual("Copied element 1.",
                         cli._format_response({"id": 1}, "copy"))


if __name__ == "__main__":
    unittest.main()
