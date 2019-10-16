import unittest
from unittest.mock import patch

from financeager.httprequests import _Proxy
from financeager.exceptions import CommunicationError
from financeager import PERIODS_TAIL, DEFAULT_HOST, DEFAULT_TIMEOUT


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
        proxy = _Proxy(http_config={"username": username, "password": password})

        with patch(
                "financeager.httprequests.requests.post",
                side_effect=self.mock_post) as post_patch:

            proxy.run("periods")

            url = "{}{}".format(DEFAULT_HOST, PERIODS_TAIL)
            kwargs = {
                "json": None,
                "auth": (username, password),
                "timeout": DEFAULT_TIMEOUT,
            }
            post_patch.assert_called_once_with(url, **kwargs)

    def test_unknown_command(self):
        self.assertRaises(ValueError, _Proxy().run, "derp")

    def test_invalid_host(self):
        proxy = _Proxy(http_config={"host": "http://weird.foodomain.nope"})

        with self.assertRaises(CommunicationError) as cm:
            proxy.run("get", period=2000, eid=1)

        error_message = cm.exception.args[0]
        self.assertTrue(error_message.startswith("Error sending request: "))
        self.assertIn("NewConnectionError", error_message)


if __name__ == "__main__":
    unittest.main()
