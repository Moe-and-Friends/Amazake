from ..config import roulette_config_pb2

from typing import List


class Responses:
    """
    A class to encapsulate response strings usable for an action.
    """

    def __init__(self, responses_config: roulette_config_pb2.RouletteConfiguration.Responses):
        self._affected_self: List[str] = responses_config.affected_self
        self._affected_other: List[str] = responses_config.affected_other
        self._unaffected_self: List[str] = responses_config.unaffected_self
        self._unaffected_other: List[str] = responses_config.unaffected_other

    @property
    def affected_self(self) -> List[str]:
        return self._affected_self

    @property
    def affected_other(self) -> List[str]:
        return self._affected_other

    @property
    def unaffected_self(self) -> List[str]:
        return self._unaffected_self

    @property
    def unaffected_other(self) -> List[str]:
        return self._unaffected_other
