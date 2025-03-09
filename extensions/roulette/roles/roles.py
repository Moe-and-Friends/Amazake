import logging

from api_extensions import roles as roles_api
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

    try:
        role = await roles_api.get_role(timeout_role, guild)
    except RuntimeError as e:
        logger.critical(f"Unable to load timeout role {timeout_role}")
        logger.critical(e)
        return None

    logger.debug(f"Loaded timeout role {role.id} ({role.name})")
    return role
