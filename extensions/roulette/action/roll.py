
from ..config import roulette_config_pb2

class Roll:

    def __init__(self, config: roulette_config_pb2.RouletteConfiguration.Roll):
        if config.HasField("weight"):
            self._weight: int = config.weight
        else:
            raise LookupError("A roll configuration was not given a weight!")
    
    @property
    def weight(self) -> int:
        return self._weight
