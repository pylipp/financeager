"""Local server proxy for direct communication."""

from .server import Server


class LocalServer(Server):
    """Subclass mocking a locally running server that shuts down (i.e. closes
    opened files) right after running a command.
    """

    def run(self, command, **kwargs):
        response = super().run(command, **kwargs)

        if command != "stop":
            # don't shutdown twice
            super().run("stop")

        return response


def proxy(**kwargs):
    return LocalServer(**kwargs)


CommunicationError = Exception
