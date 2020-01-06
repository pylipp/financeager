import unittest

from financeager import clients, config, plugin

from . import test_config


class TestClient(clients.Client):
    """Dummy class for testing."""


class CreateClientsTestCase(unittest.TestCase):
    def test_create(self):
        # Given the app configuration specifies to use the 'test' service
        app_config = config.Configuration()
        app_config._parser["SERVICE"]["name"] = "test"

        # When the create-factory is invoked
        plugin_config = test_config.TestPluginConfiguration()
        service_plugin = plugin.ServicePlugin(
            config=plugin_config,
            name="test",
            client=TestClient,
        )
        some_plugin = plugin.PluginBase(
            name="some-plugin", config=plugin_config)
        client = clients.create(
            configuration=app_config,
            sinks=None,
            plugins=[service_plugin, some_plugin],
        )

        # Then the correct client instance is returned
        self.assertIsNone(client.sinks)
        self.assertIsInstance(client, TestClient)


if __name__ == "__main__":
    unittest.main()
