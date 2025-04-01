import logging
import math
import random

from datetime import timedelta
from extensions.roulette.action.responses import Responses

from .proto import action_pb2


class Timeout:
    """
    An action representing that a user should be timed out (via Discord's native timeout)
    """

    def __init__(self, config: action_pb2.Action.Timeout):

        self.logger = logging.getLogger(__name__)
        if config.HasField("lower_bound"):
            self._lower_bound: timedelta = timedelta(minutes=config.lower_bound)
        else:
            raise LookupError("A timeout configuration did not set lower time bound!")

        if config.HasField("upper_bound"):
            self._upper_bound: timedelta = timedelta(minutes=config.upper_bound)
        else:
            raise LookupError("A timeout configuration did not set upper time bound!")

        if config.HasField("responses"):
            self._responses = Responses(config.responses)
        else:
            self._responses = None

    @property
    def lower_bound(self) -> timedelta:
        return self._lower_bound

    @property
    def upper_bound(self) -> timedelta:
        return self._upper_bound

    @property
    def responses(self) -> Responses | None:
        return self._responses

    def generate_duration(self) -> timedelta:
        lower_bound: int = math.floor(self._lower_bound.total_seconds())
        upper_bound: int = math.ceil(self._upper_bound.total_seconds())
        mute_duration = random.randint(lower_bound, upper_bound) // 60  # Always return a minute-based duration.
        return timedelta(minutes=mute_duration)
