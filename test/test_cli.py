import copy
import json
import os.path
import shlex
import tempfile
import unittest
from datetime import datetime as dt
from unittest import mock

from financeager import (DEFAULT_TABLE, RECURRENT_TABLE, cli, clients, config,
                         exceptions, plugin, setup_log_file_handler)

TEST_CONFIG_FILEPATH = "/tmp/financeager-test-config"
TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")
setup_log_file_handler(TEST_DATA_DIR)


class CliTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create test config file for client
        with open(TEST_CONFIG_FILEPATH, "w") as file:
            file.write(cls.CONFIG_FILE_CONTENT)

        cls.pocket = 1900

    def setUp(self):
        # Separate test runs by running individual test methods using distinct
        # pockets
        self.__class__.pocket += 1

        # Mocks to record output of cli.run() call
        self.info = mock.MagicMock()
        self.error = mock.MagicMock()

    def cli_run(self, command_line, log_method="info", format_args=()):
        """Wrapper around cli.run() function. Adds convenient command line
        options (pocket and config filepath). Executes the actual run() function
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
        args = shlex.split(command_line.format(*format_args))
        command = args[0]

        # Exclude option from subcommand parsers that would be confused
        if command not in ["copy", "pockets", "convert-periods-to-pocket"]:
            args.extend(["--pocket", str(self.pocket)])

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

        if command in ["get", "list", "pockets"] and log_method == "info":
            return cli._format_response(
                response,
                command,
                default_category=configuration.get_option(
                    "FRONTEND", "default_category"))

        return response


@mock.patch("financeager.DATA_DIR", None)
class CliLocalServerNoneConfigTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = ""  # service 'local' is the default anyway

    @mock.patch("tinydb.storages.MemoryStorage.write")
    def test_add_entry(self, mocked_write):
        entry_id = str(self.cli_run("add more 1337"))
        # Verify that data is written to memory
        data = mocked_write.call_args[0][0]["standard"][entry_id]
        self.assertEqual(data["name"], "more")
        self.assertEqual(data["value"], 1337.0)

    @mock.patch("builtins.print")
    @mock.patch("financeager.cli.logger.info")
    def test_pockets(self, mocked_info, mocked_print):
        cli.run(
            "pockets",
            configuration=config.Configuration(filepath=TEST_CONFIG_FILEPATH))

        mocked_info.assert_called_once_with({"pockets": []})
        mocked_print.assert_called_once_with("")

    @mock.patch("builtins.print")
    @mock.patch("financeager.localserver.Proxy.run")
    def test_str_response(self, mocked_run, mocked_print):
        # Cover the behavior of cli._format_response() given a str
        mocked_run.return_value = "response"
        cli.run(
            "pockets",
            configuration=config.Configuration(filepath=TEST_CONFIG_FILEPATH))

        self.assertListEqual(
            mocked_run.mock_calls,
            [mock.call("pockets"), mock.call("stop")])
        mocked_print.assert_called_once_with("response")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class CliLocalServerTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = """\
[SERVICE]
name = local

[FRONTEND]
default_category = no-category"""

    def test_add_entry(self):
        entry_id = self.cli_run("add entry 42")
        self.assertEqual(entry_id, 1)

        # Verify that customized default category is used
        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("no-category", response.lower())

    def test_add_entry_with_date(self):
        entry_id = self.cli_run("add something -1 -d 20-03-04 -c ' very good '")
        self.assertEqual(entry_id, 1)

        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("Date    : 2020-03-04", response)
        self.assertIn("Category: Very Good", response)

    def test_add_entry_with_tablename_and_recurrent(self):
        entry_id = self.cli_run("add stuff 1 -t standard -r")
        self.assertEqual(entry_id, 1)
        response = self.cli_run("get {}", format_args=entry_id)
        self.assertIn("stuff", response.lower())

    def test_add_recurrent_entry_without_tablename(self):
        entry_id = self.cli_run("add flowers -5 -f weekly")
        self.assertEqual(entry_id, 1)

        response = self.cli_run("get {} -t recurrent", format_args=entry_id)
        self.assertIn("Weekly", response)

    def test_get_nonexisting_entry(self):
        response = self.cli_run("get 0", log_method="error")
        self.assertEqual(response, "Invalid request: Entry not found.")

    def test_add_empty_name(self):
        response = self.cli_run('add "" 1', log_method="error")
        self.assertEqual(response, "Empty name given.")

    def test_update_empty_category(self):
        response = self.cli_run('update 1 --category ""', log_method="error")
        self.assertEqual(response, "Empty category given.")

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
        self.pocket = 1999

        self.cli_run(
            "add beans -4 -d {}-0{}-15", format_args=(self.pocket, month_nr))
        self.cli_run(
            "add chili -4 -d {}-0{}-15",
            format_args=(self.pocket, month_nr + 1))

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

    def test_convert_periods_to_pocket(self):
        period_filepath = os.path.join(TEST_DATA_DIR,
                                       "{}.json".format(self.pocket))
        period_content = {
            DEFAULT_TABLE: {
                "1": {
                    "value": 42.0,
                    "category": None,
                    "name": "entry",
                    "date": "12-28",
                },
            },
        }
        with open(period_filepath, "w") as f:
            json.dump(period_content, f)

        response = self.cli_run(
            "convert-periods-to-pocket --period-filepaths {}".format(
                period_filepath))
        self.assertEqual(response, "Converting 1 period(s)...")

        pocket_filepath = os.path.join(TEST_DATA_DIR, "main.json")
        self.assertTrue(os.path.exists(pocket_filepath))

        expected_content = copy.deepcopy(period_content)
        expected_content[DEFAULT_TABLE]["1"]["date"] = "{}-12-28".format(
            self.pocket)
        expected_content[RECURRENT_TABLE] = {}

        with open(pocket_filepath) as f:
            actual_content = json.load(f)
        self.assertDictEqual(actual_content, expected_content)

        # Verify that original period file remains unchanged
        with open(period_filepath) as f:
            disk_period_content = json.load(f)
        self.assertDictEqual(period_content, disk_period_content)

    def test_add_recurrent_entry(self):
        entry_id = self.cli_run(
            "add credit -100 --recurrent -f monthly -s 01-01")
        self.assertEqual(entry_id, 1)

        year = dt.today().year
        response = self.cli_run("get {} -r", format_args=entry_id)
        self.assertEqual(
            response, """\
Name     : Credit
Value    : -100.0
Frequency: Monthly
Start    : {}-01-01
End      : None
Category : No-Category""".format(year))

        entry_id = self.cli_run(
            "add gift -200 -t recurrent -f quarter-yearly -e 12-31")
        self.assertEqual(entry_id, 2)

        response = self.cli_run("get {} -t recurrent", format_args=entry_id)

        self.assertIn("End      : {}-12-31".format(year), response)


CONVERT_TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-convert-")


@mock.patch("financeager.DATA_DIR", CONVERT_TEST_DATA_DIR)
class CliConvertTestCase(CliTestCase):

    CONFIG_FILE_CONTENT = ""  # service 'local' is the default anyway

    def tearDown(self):
        pocket_filepath = os.path.join(CONVERT_TEST_DATA_DIR, "main.json")
        if os.path.exists(pocket_filepath):
            os.remove(pocket_filepath)

    def test_convert_non_existing_period_filepath(self):
        response = self.cli_run(
            "convert-periods-to-pocket --period-filepaths nope.json",
            log_method="error",
        )
        self.assertEqual(response,
                         "One or more non-existing filepaths:\nnope.json")

    def test_convert_invalid_period_filepath(self):
        period_filepath = os.path.join(CONVERT_TEST_DATA_DIR, "invalid.json")
        open(period_filepath, "w").close()

        response = self.cli_run(
            "convert-periods-to-pocket --period-filepaths {}".format(
                period_filepath),
            log_method="error",
        )
        lines = response.splitlines()
        self.assertEqual(lines[0], "One or more invalid filepaths:")
        self.assertTrue(lines[1].endswith("invalid.json"))
        os.remove(period_filepath)

    def test_convert_exclude_existing_main_pocket_filepath(self):
        pocket_filepath = os.path.join(CONVERT_TEST_DATA_DIR, "main.json")
        open(pocket_filepath, "w").close()
        response = self.cli_run("convert-periods-to-pocket")
        self.assertEqual(response, "Converting 0 period(s)...")

        with open(pocket_filepath) as f:
            self.assertEqual(f.read(), "")

    def test_convert_periods_to_pocket(self):
        base_year = 2000
        period_contents = []
        nr_periods = 3

        for i in range(nr_periods):
            year = base_year + i
            period_filepath = os.path.join(CONVERT_TEST_DATA_DIR,
                                           "{}.json".format(year))
            period_content = {
                DEFAULT_TABLE: {
                    "1": {
                        "value": i,
                        "category": None,
                        "name": "abc" * (i + 1),
                        "date": "12-28",
                    },
                },
            }
            with open(period_filepath, "w") as f:
                json.dump(period_content, f)

            period_contents.append(period_content[DEFAULT_TABLE]["1"])

        response = self.cli_run("convert-periods-to-pocket")
        self.assertEqual(response,
                         "Converting {} period(s)...".format(nr_periods))

        pocket_filepath = os.path.join(CONVERT_TEST_DATA_DIR, "main.json")
        self.assertTrue(os.path.exists(pocket_filepath))

        expected_content = {}
        expected_content[DEFAULT_TABLE] = {
            str(i + 1): c
            for i, c in enumerate(period_contents)
        }
        for i in range(nr_periods):
            expected_content[DEFAULT_TABLE][str(
                i + 1)]["date"] = "{}-12-28".format(base_year + i)
        expected_content[RECURRENT_TABLE] = {}

        with open(pocket_filepath) as f:
            actual_content = json.load(f)
        self.assertDictEqual(actual_content, expected_content)


class PreprocessTestCase(unittest.TestCase):
    @unittest.skip("DD.MM. not recognized as date format by dateutil")
    def test_date_format(self):
        data = {"date": "31.01."}
        cli._preprocess(data)
        self.assertDictEqual(data, {"date": "01-31"})

    def test_date(self):
        data = {"date": "02-28"}
        cli._preprocess(data)
        self.assertDictEqual(data, {"date": "{}-02-28".format(dt.today().year)})

    def test_date_format_error(self):
        data = {"date": "01_01"}
        self.assertRaises(
            exceptions.PreprocessingError,
            cli._preprocess,
            data,
        )

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


class TestPluginCliOptions(plugin.PluginCliOptions):
    def extend(self, command_parser):
        bird_parser = command_parser.add_parser("bird")
        bird_parser.add_argument("--sound")


class TestClient(clients.Client):
    def safely_run(self, command, **params):
        if command != "bird":
            raise ValueError

        if "sound" not in params:
            raise ValueError

        return True


class PluginCliOptionsTestCase(unittest.TestCase):
    def test_cli_options(self):
        test_plugin = plugin.ServicePlugin(
            name="test-plugin",
            config=None,
            cli_options=TestPluginCliOptions(),
            client=TestClient,
        )

        args = cli._parse_command(
            "bird --sound tweet".split(), plugins=[test_plugin])
        self.assertEqual(args["command"], "bird")
        self.assertEqual(args["sound"], "tweet")

        configuration = config.Configuration()
        configuration._parser["SERVICE"] = {"name": "test-plugin"}
        exit_code = cli.run(
            **args, configuration=configuration, plugins=[test_plugin])
        self.assertEqual(exit_code, cli.SUCCESS)


if __name__ == "__main__":
    unittest.main()
