import logging

import discord
from discord import Guild, Role
from typing import Optional

logger = logging.getLogger("api_extensions.roles")


async def get_role(role_id: int | str, guild: Guild) -> Optional[Role]:
    """
    A helper method to deterministically get a role from Discord.
    :param role_id: The role ID to fetch.
    :param guild: The guild to fetch the role from.
    :return: The role, as a Discord object, or None if the role doesn't exist.
    """

    role = guild.get_role(int(role_id))
    if role:
        logger.debug(f"Got role {role_id} ({role.name}) from cache.")
        return role

    # If the role isn't in the cache, attempt to fetch it from the API
    logger.debug(f"Didn't find role {role_id}, requesting from API...")
    try:
        role = await guild.fetch_role(role_id)
    except discord.NotFound:
        # This isn't (yet) a runtime error, since the role could've been deleted while the bot is running.
        logger.warning(f"Role {role_id} doesn't exist. Please check your config.")
        return None
    except discord.HTTPException as e:
        logger.critical(f"An unknown error occurred when fetching role {role_id}. Please check your environment.")
        raise RuntimeError(e)

    logger.debug(f"Fetched role {role_id} ({role.name}) from the Discord API.")
    return role
