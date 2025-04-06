import logging

from datetime import timedelta
from extensions.roulette.action.responses import Responses

from .proto import action_pb2


class TemporaryRole:
    """
    An action representing that a user should be assigned a role for a temporary duration.
    """

    def __init__(self, config: action_pb2.Action.TemporaryRole):
        self.logger = logging.getLogger(__name__)

        if config.HasField("lower_bound"):
            self._lower_bound: timedelta = timedelta(minutes=config.lower_bound)
        else:
            raise LookupError("A temporary role configuration did not set lower time bound!")

        if config.HasField("upper_bound"):
            self._upper_bound: timedelta = timedelta(minutes=config.upper_bound)
        else:
            raise LookupError("A temporary role configuration did not set upper time bound!")

        if config.HasField("role"):
            self._role: int = config.role
        else:
            raise LookupError("A temporary role configuration did not set a role to assign!")

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
    def role(self) -> int:
        return self._role

    @property
    def responses(self) -> Responses | None:
        return self._responses
