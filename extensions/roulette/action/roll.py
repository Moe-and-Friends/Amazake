from .proto import roll_pb2
from .temporary_role import TemporaryRole
from .timeout import Timeout


class Roll:

    def __init__(self, config: roll_pb2.Roll):
        if config.HasField("weight"):
            self._weight: int = config.weight
        else:
            raise LookupError("A roll configuration was not given a weight!")

        if config.action.HasField("timeout"):
            self._action = Timeout(config.action.timeout)
        elif config.action.HasField("temporary_role"):
            self._action = TemporaryRole(config.action.temporary_role)
        else:
            self._action = None

    @property
    def weight(self) -> int:
        return self._weight

    @property
    def action(self) -> TemporaryRole | Timeout | None:
        return self._action
