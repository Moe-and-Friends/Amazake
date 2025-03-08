import logging

from database.redis_client import get_redis
from discord import Member
from ..config import config

from datetime import datetime, timedelta
from discord import Message, User
from typing import Set

_redis_client = get_redis()

logger = logging.getLogger("roulette.database.redis")


# Mute functions
async def add_timeout(duration: timedelta,
                      member: Member):
    """
    Record a timeout into Redis (for future processing).
    :param duration: The duration of the timeout that will be applied.
    :param member: The member to time out.
    """

    # Calculate the time the user will be *unmuted* at.
    unmute_time = datetime.now() + duration

    # Use Redis' ZADD to store users' mute types in a ranked fashion.
    # The unmute time (in unixtime) represents the score.
    # See: https://redis.io/docs/latest/commands/zadd/
    resp = _redis_client.zadd(name=config.guild(), mapping={member.id: unmute_time.timestamp()}, ch=True)

    if resp != 1:
        return RuntimeError(f"Redis reported {resp} scores were updated for user {member.id} ({member.name})")

    logger.info(f"Recorded timeout for user {member.id} ({member.name}) expiring at {unmute_time.strftime('%c')}")
    return True


async def _fetch_unmute_candidates(guild_id) -> Set[int]:
    key = f"{guild_id}"
    data = _redis_client.zrange(key, start=0, end=-1, withscores=True)

    posix_time_now = int(datetime.now().timestamp())

    result = set()
    for user, time in data:
        if time <= posix_time_now:
            result.add(int(user))
    return result


# TODO: Fix. When there isn't a timeout detected, it won't show skipping cycle message.
async def remove_timeout(timeout_ids, bot):
    guild_ids = await _get_guild_ids()
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
