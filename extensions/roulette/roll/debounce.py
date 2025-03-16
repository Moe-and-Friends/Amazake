import logging

from cachetools import TTLCache
from datetime import datetime, timedelta

# Cache storing all users that should be temporarily debounced from sending more requests.
_CACHE = TTLCache(maxsize=5000, ttl=timedelta(minutes=1), timer=datetime.now)

logger = logging.getLogger(__name__)


def should_debounce(user_id: int) -> bool:
    """
    Debounces incoming user events against a local TTL Cache.
    :param user_id: Discord user ID (snowflake)
    :return: True if the user should be debounced (i.e. do not process), False otherwise.
    """
    # Discard aged keys in the TTLCache
    _CACHE.expire()

    # If the user isn't in the cache, add them to it and indicate user should not be debounced.
    if user_id not in _CACHE.keys():
        now = datetime.now().strftime("%c")
        logger.debug(f"Adding {user_id} to debounce cache at {now} for 1 minute")
        _CACHE[user_id] = datetime.now()
        return False

    logger.debug(f"{user_id} not in debounce cache")
    return True
