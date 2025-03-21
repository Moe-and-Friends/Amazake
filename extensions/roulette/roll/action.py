import logging
import random

from ..config import config

_WEEKS_IN_MINUTES = 10080
_DAYS_IN_MINUTES = 1440
_HOURS_IN_MINUTES = 60
_MINUTES_IN_MINUTES = 1
_TIME_CONVERSION_INTERVALS = (
    ('weeks', _WEEKS_IN_MINUTES),
    ('days', _DAYS_IN_MINUTES),
    ('hours', _HOURS_IN_MINUTES),
    ('minutes', _MINUTES_IN_MINUTES)
)

logger = logging.getLogger("roulette.roll")


class Timeout:
    def __init__(self, duration: int):
        self._duration: int = duration

    @property
    def duration(self):
        return self._duration

    @property
    def duration_label(self):
        return _convert_minutes_to_display_str(self._duration)


def fetch() -> Timeout | None:
    """
    Fetches an action (i.e. timeout) to apply to the user.
    :return: One of the action types.
    """
    # Currently, Timeout is the only action that will be applied.
    return _generate_timeout()


# TODO: Move timeout logic into its own directory.

def _generate_timeout() -> Timeout:
    # Load the list of intervals used to determine mutes.
    intervals = config.roll_timeout_intervals()
    logger.debug("Loaded {count} intervals.".format(count=int(len(intervals))))

    # First, select an interval to load
    # Create the bounds tuples and their respective weights
    bounds = [interval["bound"] for interval in intervals]
    weights = [int(interval["weight"]) for interval in intervals]
    interval = random.choices(bounds, weights=weights, k=1)[0]

    # From the interval, randomly select a time.
    # The interval is a Tuple[lower_bound: str, upper_bound: str]
    lower_bound = _convert_interval_str_to_minutes(interval["lower"])
    upper_bound = _convert_interval_str_to_minutes(interval["upper"])

    mute_duration = random.randint(lower_bound, upper_bound)
    logger.debug(
        "Selected mute duration: ({mute_duration}) from lower bound: ({lower_bound}) and upper bound: ({upper_bound}).".format(
            mute_duration=_convert_minutes_to_display_str(mute_duration),
            lower_bound=_convert_minutes_to_display_str(lower_bound),
            upper_bound=_convert_minutes_to_display_str(upper_bound)))

    return Timeout(mute_duration)


def _convert_interval_str_to_minutes(interval: str) -> int:
    # Strip out non-numeric characters
    time = int("".join(filter(str.isdigit, interval)))
    if interval.endswith("m"):
        return time * _MINUTES_IN_MINUTES  # Base case
    elif interval.endswith("h"):
        return time * _HOURS_IN_MINUTES
    elif interval.endswith("d"):
        return time * _DAYS_IN_MINUTES
    elif interval.endswith("w"):
        return time * _WEEKS_IN_MINUTES


def _convert_minutes_to_display_str(minutes: int, granularity=2) -> str:
    if minutes == 0:
        return "0 minutes"
    result = list()
    for name, count in _TIME_CONVERSION_INTERVALS:
        value = minutes // count
        if value:
            minutes -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    start, _, end = ', '.join(result[:granularity]).rpartition(',')
    return start + " and" + end if start else end
