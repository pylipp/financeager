import logging
import unittest

from financeager import LOGGER, init_logger


class InitLoggerTestCase(unittest.TestCase):
    def test_init_library_logger(self):
        library_logger = logging.getLogger("library")
        library_logger.addHandler(logging.NullHandler())

        updated_logger = init_logger("library")
        self.assertEqual(updated_logger.level, logging.DEBUG)
        self.assertEqual(updated_logger.parent, LOGGER)
        self.assertTrue(updated_logger.propagate)
