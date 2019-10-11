"""Utiliary classes for testing."""
from financeager import communication, config


class Client(communication.Client):
    """Implementation that assigns dummy functions for the 'out' argument,
    and holds a default configuration (meaning it communicates with the 'none'
    service.
    The underlying LocalServer is patched to store data in memory instead of in
    financeager.DATA_DIR.
    """

    def __init__(self):
        f = lambda s: None
        super().__init__(
            configuration=config.Configuration(),
            out=communication.Client.Out(f, f))

        self.proxy._period_kwargs["data_dir"] = None
