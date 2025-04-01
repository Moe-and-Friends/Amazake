from typing import List

from .proto import action_pb2


class Responses:
    """
    A class to encapsulate response strings usable for an action.
    """

    def __init__(self, responses: action_pb2.Action.Responses):
        self._affected_self: List[str] = responses.affected_self
        self._affected_other: List[str] = responses.affected_other
        self._unaffected_self: List[str] = responses.unaffected_self
        self._unaffected_other: List[str] = responses.unaffected_other

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
