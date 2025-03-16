import logging

from cachetools import TTLCache
from datetime import datetime, timedelta

# Cache that prevents the unmute loop from spamming itself
_CACHE = TTLCache(maxsize=1, ttl=timedelta(seconds=1), timer=datetime.now)
_KEY = "unmute"

logger = logging.getLogger(__name__)


def should_debounce() -> bool:
    """
    Debounces incoming unmute events against a local TTL Cache.
    :return: True if the unmute should be debounced (i.e. do not process), False otherwise.
    """
    # Discard aged keys in the TTLCache
    _CACHE.expire()
    if _KEY not in _CACHE.keys():
        logger.debug(f"Event detected, now debouncing unmute events for 1 second.")
        _CACHE[_KEY] = True
        return False

    logger.debug("Debouncing unmute event.")
    return True
