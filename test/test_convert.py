import json
import os.path
import tempfile
import unittest
from unittest import mock

from financeager import (DEFAULT_POCKET_NAME, DEFAULT_TABLE, RECURRENT_TABLE,
                         convert)

TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class ConvertTestCase(unittest.TestCase):
    POCKET_FILEPATH = os.path.join(TEST_DATA_DIR,
                                   "{}.json".format(DEFAULT_POCKET_NAME))

    def tearDown(self):
        if os.path.exists(self.POCKET_FILEPATH):
            os.remove(self.POCKET_FILEPATH)

    def test_convert_no_period(self):
        convert.run(period_filepaths=[])
        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            self.assertEqual(f.read(), "")

    def test_convert_empty_period(self):
        expected_content = {DEFAULT_TABLE: {}, RECURRENT_TABLE: {}}

        period_filepath = os.path.join(TEST_DATA_DIR, "1234.json")
        with open(period_filepath, "w") as f:
            json.dump(expected_content, f)
        convert.run(period_filepaths=[period_filepath])

        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            actual_content = json.load(f)
        self.assertDictEqual(actual_content, expected_content)

    def test_convert_single_period(self):
        period_content = {
            DEFAULT_TABLE: {
                "1": {
                    "value": 42.0,
                    "category": None,
                    "name": "entry",
                    "date": "12-28",
                },
            },
            RECURRENT_TABLE: {
                "1": {
                    "value": -500.0,
                    "category": None,
                    "name": "rent",
                    "start": "01-01",
                    "end": "12-31",
                    "frequency": "monthly",
                },
            },
        }

        period_filepath = os.path.join(TEST_DATA_DIR, "1235.json")
        with open(period_filepath, "w") as f:
            json.dump(period_content, f)
        convert.run(period_filepaths=[period_filepath])

        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        expected_content = period_content.copy()
        expected_content[DEFAULT_TABLE]["1"]["date"] = "1235-12-28"
        expected_content[RECURRENT_TABLE]["1"]["start"] = "1235-01-01"
        expected_content[RECURRENT_TABLE]["1"]["end"] = "1235-12-31"

        with open(self.POCKET_FILEPATH) as f:
            actual_content = json.load(f)

        self.assertDictEqual(actual_content, expected_content)

    def test_convert_multiple_periods(self):
        period_content = {
            DEFAULT_TABLE: {
                "1": {
                    "value": 42.0,
                    "category": None,
                    "name": "entry",
                    "date": "12-28",
                },
            },
            RECURRENT_TABLE: {
                "1": {
                    "value": -500.0,
                    "category": None,
                    "name": "rent",
                    "start": "01-01",
                    "end": "12-31",
                    "frequency": "monthly",
                },
            },
        }
        period_filepath = os.path.join(TEST_DATA_DIR, "1236.json")
        with open(period_filepath, "w") as f:
            json.dump(period_content, f)
        period_filepaths = [period_filepath]

        expected_content = period_content.copy()
        expected_content[DEFAULT_TABLE]["1"]["date"] = "1236-12-28"
        expected_content[RECURRENT_TABLE]["1"]["start"] = "1236-01-01"
        expected_content[RECURRENT_TABLE]["1"]["end"] = "1236-12-31"

        period_content = {
            DEFAULT_TABLE: {
                "1": {
                    "value": -5.0,
                    "category": "food",
                    "name": "burrito",
                    "date": "03-04",
                },
            },
        }
        period_filepath = os.path.join(TEST_DATA_DIR, "1237.json")
        with open(period_filepath, "w") as f:
            json.dump(period_content, f)
        period_filepaths.append(period_filepath)

        expected_content[DEFAULT_TABLE]["2"] =\
            period_content[DEFAULT_TABLE]["1"].copy()
        expected_content[DEFAULT_TABLE]["2"]["date"] = "1237-03-04"

        convert.run(period_filepaths=period_filepaths)

        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            actual_content = json.load(f)

        self.assertDictEqual(actual_content, expected_content)


if __name__ == "__main__":
    unittest.main()
