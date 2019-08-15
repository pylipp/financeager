#!/usr/bin/env python

from os import environ
import tempfile
import unittest
from unittest import mock

from financeager.fflask import create_app
import financeager


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_warning',
        'test_debug',
        'test_data_dir_env_variable',
    ]
    suite.addTest(unittest.TestSuite(map(CreateAppNoDataDirTestCase, tests)))
    return suite


# Patch DATA_DIR to avoid having it created/interfering with logs on actual
# machine
TEST_DATA_DIR = tempfile.mkdtemp(prefix="financeager-")


@mock.patch("financeager.DATA_DIR", TEST_DATA_DIR)
class CreateAppNoDataDirTestCase(unittest.TestCase):
    @mock.patch("financeager.fflask.logger.warning")
    def test_warning(self, mocked_warning):
        create_app()
        mocked_warning.assert_called_once_with(
            "'data_dir' not given. Application data is stored in "
            "memory and is lost when the flask app terminates. Set "
            "the environment variable FINANCEAGER_DATA_DIR "
            "accordingly for persistent data storage.")

    def test_debug(self):
        app = create_app(config={"DEBUG": True})
        self.assertTrue(app.debug)
        self.assertEqual(financeager.LOGGER.handlers[0].level, 10)

    def test_data_dir_env_variable(self):
        data_dir = tempfile.mkdtemp(prefix="financeager-")
        environ["FINANCEAGER_DATA_DIR"] = data_dir
        with mock.patch("os.makedirs") as mocked_makedirs:
            create_app(data_dir=None)
            # First call is from inside setup_log_file_handler()
            self.assertEqual(mocked_makedirs.call_count, 2)
            mocked_makedirs.assert_called_with(data_dir, exist_ok=True)
        del environ["FINANCEAGER_DATA_DIR"]


if __name__ == "__main__":
    unittest.main()
