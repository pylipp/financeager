"""Utiliary classes for testing."""
from financeager import communication, config


class Client(communication.Client):
    """Implementation that assigns dummy functions for the 'out' argument,
    interfaces with the 'none' service and holds a default configuration."""

    def __init__(self):
        f = lambda s: None
        super().__init__(
            configuration=config.Configuration(),
            service_name="none",
            out=communication.Client.Out(f, f))
