import unittest
from unittest import mock
import time

from financeager.config import Configuration, InvalidConfigError


class ConfigTestCase(unittest.TestCase):
    def test_sections(self):
        config = Configuration()
        self.assertSetEqual(
            set(config.sections()), {"SERVICE", "FRONTEND", "SERVICE:FLASK"})

    def test_load_custom_config_file(self):
        # create custom config file, modify service name
        filepath = "/tmp/{}".format(int(time.time()))
        with open(filepath, "w") as file:
            file.write("[SERVICE]\nname = flask\n")

        config = Configuration(filepath=filepath)
        self.assertEqual(config.get("SERVICE", "name"), "flask")

    @mock.patch("financeager.CONFIG_FILEPATH", "/tmp/non-existing-config")
    def test_get_option(self):
        config = Configuration()
        self.assertEqual(config.get_option("SERVICE", "name"), "none")
        self.assertDictEqual(config.get_option("SERVICE"), {"name": "none"})

    def test_invalid_config(self):
        filepath = "/tmp/{}".format(int(time.time()))

        for content in (
                "[SERVICE]\nname = sillyservice\n",
                "[FRONTEND]\ndefault_category = ",
        ):
            with open(filepath, "w") as file:
                file.write(content)
            self.assertRaises(
                InvalidConfigError, Configuration, filepath=filepath)

    def test_nonexisting_config_filepath(self):
        filepath = "/tmp/{}".format(time.time())
        with self.assertRaises(InvalidConfigError) as cm:
            Configuration(filepath=filepath)
        self.assertTrue(
            cm.exception.args[0].endswith("Config filepath does not exist!"))


if __name__ == "__main__":
    unittest.main()
