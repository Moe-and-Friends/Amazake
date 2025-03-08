import logging

from database.redis_client import get_redis
from ..config import config
from .action import get_timeout_roles

from datetime import datetime, timedelta
from discord import Message, User
from typing import Set

_redis_client = get_redis()

logger = logging.getLogger("roulette.database")


# Mute functions
async def add_timeout(duration: timedelta,
                      message: Message,
                      user: User) -> bool:
    key = str(message.guild.id)
    unmute_time = int(datetime.now() + duration)

    # Use Redis' ZADD to store users' mute types in a ranked fashion.
    # The unmute time (in unixtime) represents the score.
    # See: https://redis.io/docs/latest/commands/zadd/
    resp = _redis_client.zadd(name=key, mapping={user.id: unmute_time}, ch=True)

    # If no scores were added, the timeout wasn't added for some reason.
    if resp == 0:
        return False

    logger.warning(f"{resp} scores got updated")
    return True


# Unmute functions
async def _get_guild_ids() -> Set[int]:
    cursor = 0

    guild_keys = set()
    guild_ids = set()

    while True:
        cursor, partial_keys = _redis_client.scan(cursor=cursor, match='*')
        guild_keys.update(partial_keys)

        if cursor == 0:
            break

    for key in guild_keys:
        key = key.decode('utf-8')
        key = key.removeprefix(config_key)
        guild_ids.add(int(key))

    return guild_ids


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
