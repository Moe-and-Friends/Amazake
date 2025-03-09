import logging

import discord
from discord import Guild
from discord.ext.commands import Bot
from typing import Optional

logger = logging.getLogger("api_extensions.guilds")


async def get_guild(guild_id: int | str, bot: Bot) -> Optional[Guild]:
    """
    A helper method to deterministically get a Guild from Discord.
    :param guild_id: The guild ID to fetch.
    :param bot: The bot to fetch the guild from.
    :return: The Guild, as a Discord object, or None if it doesn't exist.
    """
    guild = bot.get_guild(int(guild_id))
    if guild:
        logger.debug(f"Got guild {guild_id} ({guild.name}) from the cache.")
        return guild

    try:
        guild = await bot.fetch_guild(guild_id)
    except discord.NotFound:
        # This isn't (yet) a runtime error, since the guild could've been deleted while the bot is running.
        logger.warning(f"Guild {guild_id} doesn't exist. Please check your config.")
        return None
    except discord.HTTPException as e:
        logger.critical(f"An unknown error occurred when fetching guild {guild_id}. Please check your environment.")
        raise RuntimeError(e)

    logger.debug(f"Fetched guild {guild_id} ({guild.name}) from the Discord API.")
    return guild
