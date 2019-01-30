#!/usr/bin/env python

import unittest
from unittest import mock

from financeager.fflask import create_app


def suite():
    suite = unittest.TestSuite()
    tests = [
        'test_warning',
    ]
    suite.addTest(unittest.TestSuite(map(CreateAppNoDataDirTestCase, tests)))
    return suite


class CreateAppNoDataDirTestCase(unittest.TestCase):
    @mock.patch("financeager.fflask.logger.warning")
    def test_warning(self, mocked_warning):
        create_app()
        mocked_warning.assert_called_once_with(
            "'data_dir' not given. Application data is stored in "
            "memory and is lost when the flask app terminates.")


if __name__ == "__main__":
    unittest.main()
