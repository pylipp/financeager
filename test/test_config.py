import unittest
import os.path
import time

from financeager.config import CONFIG_DIR, Configuration


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_config_dir_exists',
            'test_sections',
            'test_load_custom_config_file',
            ]
    suite.addTest(unittest.TestSuite(map(ConfigTestCase, tests)))
    return suite


class ConfigTestCase(unittest.TestCase):
    def test_config_dir_exists(self):
        self.assertTrue(os.path.isdir(CONFIG_DIR))

    def test_sections(self):
        config = Configuration()
        self.assertSetEqual(set(config.sections()), {"SERVICE", "FRONTEND",
            "SERVICE:FLASK"})

    def test_load_custom_config_file(self):
        # create custom config file, modify service name
        filepath = "/tmp/{}".format(int(time.time()))
        custom_config = Configuration(filepath=filepath)
        custom_config.set("SERVICE", "name", "flask")
        with open(filepath, "w") as f:
            custom_config.write(f)

        config = Configuration(filepath=filepath)
        self.assertEqual(config.get("SERVICE", "name"), "flask")


if __name__ == "__main__":
    unittest.main()
