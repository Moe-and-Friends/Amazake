_WEEKS_IN_SECONDS = 604800
_DAYS_IN_SECONDS = 86400
_HOURS_IN_SECONDS = 3600
_MINUTES_IN_SECONDS = 60
_SECONDS_IN_SECONDS = 1
_TIME_CONVERSION_INTERVALS = (
    ('weeks', _WEEKS_IN_SECONDS),
    ('days', _DAYS_IN_SECONDS),
    ('hours', _HOURS_IN_SECONDS),
    ('minutes', _MINUTES_IN_SECONDS),
    ('seconds', _SECONDS_IN_SECONDS)
)


def convert_interval_str_to_seconds(interval: str) -> int:
    # Strip out non-numeric characters
    time = int("".join(filter(str.isdigit, interval)))
    if interval.endswith("s"):
        return time * _SECONDS_IN_SECONDS
    if interval.endswith("m"):
        return time * _MINUTES_IN_SECONDS  # Base case
    elif interval.endswith("h"):
        return time * _HOURS_IN_SECONDS
    elif interval.endswith("d"):
        return time * _DAYS_IN_SECONDS
    elif interval.endswith("w"):
        return time * _WEEKS_IN_SECONDS


def convert_seconds_to_display_str(seconds: int, granularity=3) -> str:
    if seconds == 0:
        return "0 seconds"
    result = list()
    for name, count in _TIME_CONVERSION_INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    start, _, end = ', '.join(result[:granularity]).rpartition(',')
    return start + " and" + end if start else end
