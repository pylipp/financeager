"""Local server proxy for direct communication (client and server reside in
common process)."""

from . import exceptions, init_logger, server

logger = init_logger(__name__)


class Proxy(server.Server):
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
            raise exceptions.CommunicationError("Unexpected error")

        if "error" in response:
            raise exceptions.InvalidRequest("Invalid request: {}".format(
                response["error"]))

        return response
