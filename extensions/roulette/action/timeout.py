from .responses import Responses
from ..config import roulette_config_pb2

from datetime import timedelta
from typing import Optional


# TODO: Move individual configurations to their own proto files.

class Timeout:
    """
    An action representing that a user should be timed out (via Discord's native timeout)
    """

    def __init__(self, config: roulette_config_pb2.RouletteConfiguration.Roll.Action.Timeout):
        if config.HasField("lower_bound"):
            self._lower_bound: timedelta = timedelta(minutes=config.lower_bound)
        else:
            raise LookupError("A timeout configuration did not set lower time bound!")

        if config.HasField("upper_bound"):
            self._upper_bound: timedelta = timedelta(minutes=config.upper_bound)
        else:
            raise LookupError("A timeout configuration did not set upper time bound!")

        self._responses: Optional[Responses] = Responses(config.responses) if config.HasField("responses") else None

    @property
    def lower_bound(self) -> timedelta:
        return self._lower_bound

    @property
    def upper_bound(self) -> timedelta:
        return self._upper_bound

    @property
    def responses(self) -> Optional[Responses]:
        return self._responses
