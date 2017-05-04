import unittest
import os.path

from financeager.config import CONFIG, CONFIG_DIR


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists'
            ,'test_config_sections'
            ]
    suite.addTest(unittest.TestSuite(map(ConfigTestCase, tests)))
    return suite


class ConfigTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        self.assertTrue(os.path.isdir(CONFIG_DIR))

    def test_config_sections(self):
        self.assertSetEqual(set(CONFIG.sections()), {"SERVICE", "DATABASE"})


if __name__ == "__main__":
    unittest.main()
