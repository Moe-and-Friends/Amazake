from .timeout import Timeout
from ..config import roulette_config_pb2

from typing import Optional


class Roll:

    def __init__(self, config: roulette_config_pb2.RouletteConfiguration.Roll):
        if config.HasField("weight"):
            self._weight: int = config.weight
        else:
            raise LookupError("A roll configuration was not given a weight!")

        if config.action.WhichOneof("action") is roulette_config_pb2.RouletteConfiguration.Roll.Action.Timeout:
            self._action = Timeout(config.action.timeout)
        # TODO: Support other Action types besides Timeout.
        else:
            self._action = None

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def action(self) -> Timeout | None:
        return self._action
