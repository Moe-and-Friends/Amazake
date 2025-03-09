import logging

import discord
from discord import Guild, Member
from typing import Optional

logger = logging.getLogger("api_extensions.members")


async def get_member(member_id: int | str, guild: Guild) -> Optional[Member]:
    """
    A helper method to deterministically get a Member from Discord.
    :param member_id: The member ID to fetch.
    :param guild: The guild to fetch the member from.
    :return: The member, as a Discord object, or None if it doesn't exist.
    """
    member = guild.get_member(int(member_id))
    if member:
        logger.debug(f"Got member {member_id} ({member.name}) from the cache.")
        return member

    try:
        member = await guild.fetch_member(member_id)
    except discord.Forbidden:
        # This isn't (yet) a runtime error. since the guild could've just kicked the bot.
        logger.warning(f"Bot does not have access to guild {guild.id} ({guild.name}).")
        raise None
    except discord.NotFound:
        # This isn't (yet) a runtime error, since the member could've left the guild.
        logger.warning(f"Member {member} doesn't exist. Did they leave?")
        return None
    except discord.HTTPException as e:
        logger.critical(f"An unknown error occurred when fetching member {member_id}. Please check your environment.")
        raise RuntimeError(e)

    logger.debug(f"Fetched member {member.id} ({member.name}) from the Discord API.")
    return member
