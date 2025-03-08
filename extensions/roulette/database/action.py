import logging

from ..config import config
from typing import Set
from discord import Guild, Role, NotFound

logger = logging.getLogger("roulette.database")


async def get_timeout_roles(guild: Guild) -> Set[Role]:
    """
    Fetches the :Role:s that should be applied on timeout.
    :param guild: The Guild to fetch roles from.
    :return: A set of
    """
    role_ids = config.timeout_roles()
    timeout_roles = set()

    for role_id in role_ids:
        role = guild.get_role(int(role_id))
        try:
            if not role:
                logger.warning(f"Role {role_id} not found in cache, fetching from the Discord API...")
                role = await guild.fetch_role(int(role_id))
        except NotFound:
            raise NotFound(f"Role {role_id} not found from API. Check your configuration!")

        if role:
            timeout_roles.add(role)
        else:
            logger.warning(f"")

    if len(timeout_roles) == 0:
        raise ValueError("No timeout roles found. Check your configuration!")
    return timeout_roles
