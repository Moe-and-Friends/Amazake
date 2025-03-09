import logging

from cachetools import TTLCache
from datetime import datetime, timedelta

# Cache that prevents the unmute loop from spamming itself
_CACHE = TTLCache(maxsize=1, ttl=timedelta(seconds=1), timer=datetime.now)
_KEY = "unmute"

logger = logging.getLogger("roulette.unmute")


def should_debounce() -> bool:
    """
    Debounces incoming user events against a local TTL Cache.
    :param user_id: Discord user ID (snowflake)
    :return: True if the user should be debounced (i.e. do not process), False otherwise.
    """
    # Discard aged keys in the TTLCache
    _CACHE.expire()
    if _KEY not in _CACHE.keys():
        logger.debug(f"Event detected, now debouncing unmute events for 1 second.")
        _CACHE[_KEY] = True
        return False

    logger.debug("Debouncing unmute event.")
    return True
