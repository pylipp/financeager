"""Utiliary classes for testing."""
from financeager import communication, config


class Client(communication.Client):
    """Implementation that assigns dummy functions for the 'out' argument, and
    the default configuration."""

    def __init__(self, *, service_name):
        f = lambda s: None
        super().__init__(
            configuration=config.Configuration(),
            service_name=service_name,
            out=communication.Client.Out(f, f))
