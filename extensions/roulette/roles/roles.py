import logging

from discord import Guild, Role
from typing import Optional

from ..config import config

logger = logging.getLogger("roulette.roles")


async def get_timeout_role(guild: Guild) -> Optional[Role]:
    """
    :param guild: A Guild to fetch the role from.
    :return: Returns a Discord role associated with an ID, or None if it can't be found.
    """
    timeout_role = config.timeout_role()
    if not timeout_role:
        return None

    role = guild.get_role(int(timeout_role))
    # If the role isn't in the cache, attempt to fetch it from the API
    if not role:
        logger.debug(f"Didn't find role {timeout_role}, requesting from API...")
        role = await guild.fetch_role(int(timeout_role))

    # If the role still wasn't found, it likely doesn't exist.
    if not role:
        return None

    return role
