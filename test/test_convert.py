import json
import os.path
import tempfile
import unittest
from unittest import mock

from financeager import DEFAULT_TABLE, convert

TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class ConvertTestCase(unittest.TestCase):
    POCKET_FILEPATH = os.path.join(TEST_DATA_DIR, "main.json")

    def tearDown(self):
        if os.path.exists(self.POCKET_FILEPATH):
            os.remove(self.POCKET_FILEPATH)

    def test_convert_no_period(self):
        convert.run(period_filepaths=[])
        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            self.assertEqual(f.read(), "")

    def test_convert_empty_period(self):
        expected_content = {DEFAULT_TABLE: {}, "recurrent": {}}

        period_filepath = os.path.join(TEST_DATA_DIR, "1234.json")
        with open(period_filepath, "w") as f:
            json.dump(expected_content, f)
        convert.run(period_filepaths=[period_filepath])

        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            actual_content = json.load(f)
        self.assertDictEqual(actual_content, expected_content)

    def test_convert_single_period(self):
        expected_content = {
            DEFAULT_TABLE: {
                "1": {
                    "value": 42.0,
                    "category": None,
                    "name": "entry",
                    "date": "12-28",
                },
            },
            "recurrent": {
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
            json.dump(expected_content, f)
        convert.run(period_filepaths=[period_filepath])

        self.assertTrue(os.path.exists(self.POCKET_FILEPATH))

        with open(self.POCKET_FILEPATH) as f:
            actual_content = json.load(f)
        self.assertDictEqual(actual_content, expected_content)


if __name__ == "__main__":
    unittest.main()
