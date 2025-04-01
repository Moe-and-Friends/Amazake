from .proto import roll_pb2
from .timeout import Timeout


class Roll:

    def __init__(self, config: roll_pb2.Roll):
        if config.HasField("weight"):
            self._weight: int = config.weight
        else:
            raise LookupError("A roll configuration was not given a weight!")

        if config.action.HasField("timeout"):
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
