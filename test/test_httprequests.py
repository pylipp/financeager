import unittest
from unittest.mock import patch

from financeager.httprequests import _Proxy
from financeager import PERIODS_TAIL


def suite():
    suite = unittest.TestSuite()
    tests = ['test_username_password']
    suite.addTest(unittest.TestSuite(map(HttpRequestProxyTestCase, tests)))
    return suite


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

        with patch("financeager.httprequests.requests.post",
                   side_effect=self.mock_post) as post_patch:

            proxy.run("list")

            url = "http://{}{}".format(_Proxy.DEFAULT_HOST, PERIODS_TAIL)
            kwargs = {
                "data": None,
                "auth": (username, password),
                "timeout": _Proxy.DEFAULT_TIMEOUT,
            }
            post_patch.assert_called_once_with(url, **kwargs)


if __name__ == "__main__":
    unittest.main()
