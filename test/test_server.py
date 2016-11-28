# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.server import Server, CONFIG_DIR
import os.path


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ]
    suite.addTest(unittest.TestSuite(map(StartServerTestCase, tests)))
    return suite

class StartServerTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        server = Server()
        self.assertTrue(os.path.isdir(CONFIG_DIR))

if __name__ == '__main__':
    unittest.main()
