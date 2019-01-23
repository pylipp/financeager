import unittest
import time

from financeager.config import Configuration


def suite():
    suite = unittest.TestSuite()
    tests = [
            'test_sections',
            'test_load_custom_config_file',
            'test_get_option',
            ]
    suite.addTest(unittest.TestSuite(map(ConfigTestCase, tests)))
    return suite


class ConfigTestCase(unittest.TestCase):
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

    def test_get_option(self):
        config = Configuration()
        self.assertEqual(config.get_option("SERVICE", "name"), "none")
        self.assertDictEqual(config.get_option("SERVICE"), {"name": "none"})


if __name__ == "__main__":
    unittest.main()
