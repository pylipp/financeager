import unittest

from financeager import clients, plugin, config

from . import test_config


class TestClient(clients.Client):
    def __init__(self, *, configuration, sinks):
        super().__init__(sinks=sinks)
        self.configuration = configuration


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
        client = clients.create(
            configuration=app_config,
            sinks=None,
            plugins=[service_plugin],
        )

        # Then the correct client instance is returned
        self.assertIsNone(client.sinks)
        self.assertIsInstance(client, TestClient)


if __name__ == "__main__":
    unittest.main()
