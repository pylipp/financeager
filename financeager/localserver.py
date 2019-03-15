"""Local server proxy for direct communication (client and server reside in
common process)."""

from .server import Server
from .exceptions import InvalidRequest, CommunicationError
from . import init_logger

logger = init_logger(__name__)


class LocalServer(Server):
    """Subclass mocking a locally running server. Convenient for testing"""

    def run(self, command, **kwargs):
        """Run command on local server, and shut it down immediately. Any
        unexpected exceptions will be propagated upwards.

        :raises: InvalidRequest on invalid request
                 CommunicationError on unexpected server error
        """
        try:
            response = super().run(command, **kwargs)

            if command != "stop":
                # don't shutdown twice
                super().run("stop")
        except Exception as e:
            logger.exception("Unexpected error")
            raise CommunicationError("Unexpected error")

        # stop-command is expected to return None
        if response is not None and "error" in response:
            raise InvalidRequest("Invalid request: {}".format(
                response["error"]))

        return response


def proxy(**kwargs):
    return LocalServer(**kwargs)
