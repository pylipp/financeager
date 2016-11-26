# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from financeager.period import Period

def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_default_name'
            ]
    suite.addTest(unittest.TestSuite(map(CreateEmptyPeriodTestCase, tests)))
    return suite

class CreateEmptyPeriodTestCase(unittest.TestCase):
    def test_default_name(self):
        period = Period()
        self.assertEqual(period.name, "2016")

if __name__ == '__main__':
    unittest.main()
