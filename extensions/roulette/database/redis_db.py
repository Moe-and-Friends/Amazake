import logging

from database.redis_client import get_redis

from datetime import datetime
from typing import Set

_redis_client = get_redis()

logger = logging.getLogger("roulette.database.redis")


# TODO: Fix. When there isn't a timeout detected, it won't show skipping cycle message.
async def remove_timeout(timeout_ids, bot):
    # TODO: Remove empty set here.
    guild_ids = set()
    for guild_id in guild_ids:
        unmute_candidates = await _fetch_unmute_candidates(guild_id)

        if not unmute_candidates:
            logger.info("No records fetched. Skipping cycle.")
            return

        guild = bot.get_guild(guild_id)
        timeout_roles = get_timeout_roles(guild)

        for candidate in unmute_candidates:
            member = await guild.fetch_member(candidate)
            if not timeout_ids.isdisjoint(set([str(role.id) for role in member.roles])):
                logger.info(f"Removed timeout for {member}")
                await member.remove_roles(timeout_roles, reason="Timeout expired")
