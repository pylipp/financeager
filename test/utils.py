"""Utiliary classes for testing."""
from financeager import communication, config


class Client(communication.LocalServerClient):
    """Implementation that assigns dummy sinks to consume the client's output.
    The underlying LocalServer is patched to store data in memory instead of in
    financeager.DATA_DIR.
    """

    def __init__(self):
        f = lambda s: None
        super().__init__(
            configuration=config.Configuration(),
            sinks=communication.Client.Sinks(f, f))

        self.proxy._period_kwargs["data_dir"] = None
