"""Local server proxy for direct communication (client and server reside in
common process)."""

from .server import Server
from .exceptions import InvalidRequest


class LocalServer(Server):
    """Subclass mocking a locally running server. Convenient for testing"""

    def run(self, command, **kwargs):
        """Run command on local server, and shut it down immediately. Any
        unexpected exceptions will be propagated upwards.

        :raises: InvalidRequest on invalid request
        """
        response = super().run(command, **kwargs)

        if command != "stop":
            # don't shutdown twice
            super().run("stop")

        if "error" in response:
            raise InvalidRequest(
                "Invalid request: {}".format(response["error"]))

        return response


def proxy(**kwargs):
    return LocalServer(**kwargs)
