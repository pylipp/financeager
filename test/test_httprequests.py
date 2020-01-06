import unittest
from unittest.mock import patch

from financeager import DEFAULT_HOST, PERIODS_TAIL
from financeager.exceptions import CommunicationError
from financeager.httprequests import Proxy as HttpProxy


class HttpRequestProxyTestCase(unittest.TestCase):
    def mock_post(*args, **kwargs):
        """Mock a Response object returned by requests.post."""

        class MockResponse:
            ok = True

            def json(self):
                return {}

        return MockResponse()

    def test_username_password(self):
        username = "noob"
        password = 123456
        timeout = 1
        proxy = HttpProxy(http_config={
            "username": username,
            "password": password,
            "timeout": timeout,
        })

        with patch(
                "financeager.httprequests.requests.post",
                side_effect=self.mock_post) as post_patch:

            proxy.run("periods")

            url = "{}{}".format(DEFAULT_HOST, PERIODS_TAIL)
            kwargs = {
                "json": None,
                "auth": (username, password),
                "timeout": timeout,
            }
            post_patch.assert_called_once_with(url, **kwargs)

    def test_unknown_command(self):
        self.assertRaises(ValueError, HttpProxy({"timeout": 1}).run, "derp")

    def test_invalid_host(self):
        proxy = HttpProxy({"host": "http://weird.foodomain.nope", "timeout": 5})

        with self.assertRaises(CommunicationError) as cm:
            proxy.run("get", period=2000, eid=1)

        error_message = cm.exception.args[0]
        self.assertTrue(error_message.startswith("Error sending request: "))
        self.assertIn("NewConnectionError", error_message)


if __name__ == "__main__":
    unittest.main()
