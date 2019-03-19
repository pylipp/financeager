"""Local server proxy for direct communication (client and server reside in
common process)."""

from .server import Server
from .exceptions import InvalidRequest, CommunicationError
from . import init_logger

logger = init_logger(__name__)


class LocalServer(Server):
    """Subclass mocking a locally running server. Convenient for testing"""

    def run(self, command, **kwargs):
        """Run command on local server. Exceptions are propagated upwards. Call
        run('stop') as last operation to properly close the databases before
        exiting the process.

        :raises: InvalidRequest on invalid request
                 CommunicationError on unexpected server error
        """
        try:
            response = super().run(command, **kwargs)
        except Exception:
            logger.exception("Unexpected error")
            raise CommunicationError("Unexpected error")

        if "error" in response:
            raise InvalidRequest("Invalid request: {}".format(
                response["error"]))

        return response


def proxy(**kwargs):
    return LocalServer(**kwargs)
