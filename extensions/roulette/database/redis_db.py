import logging

from Redis.redis_config import get_redis
from ..config import config
from .action import fetch_timeout_roles

from datetime import datetime, timedelta
from discord import Member, Message
from typing import Set

_redis_client = get_redis()

logger = logging.getLogger("roulette.database")


# Mute functions
# TODO: Check for successful update
async def _upload_timeout(duration: timedelta,
                          message: Message,
                          target: Member) -> int:

    key = config.redis_key_const() + str(message.guild.id)

    time_unmute = datetime.now() + duration
    posix_time_unmute = int(time_unmute.timestamp())

    resp = _redis_client.zadd(key, {target.id: posix_time_unmute})
    return resp


async def _apply_timeout_roles(target, duration_label):
    timeout_ids = config.timeout_roles()

    for timeout_id in timeout_ids:
        role = target.guild.get_role(int(timeout_id))

        if role:
            await target.add_roles(role, reason=f"Adding role for {duration_label} timeout")


async def add_timeout(target, duration_label, duration, message):
    await _upload_timeout(duration, message, target)


# Unmute functions
async def _get_guild_ids() -> Set[int]:
    cursor = 0
    pattern = config.redis_key_const() + '*'

    guild_keys = set()
    guild_ids = set()

    while True:
        cursor, partial_keys = _redis_client.scan(cursor=cursor, match=pattern)
        guild_keys.update(partial_keys)

        if cursor == 0:
            break

    for key in guild_keys:
        guild_ids.add(int(key[22:]))

    return guild_ids


async def _fetch_candidates(guild_id) -> Set[int]:
    key = f"{config.redis_key_const()}{guild_id}"
    data = _redis_client.zrange(key, start=0, end=-1, withscores=True)

    posix_time_now = int(datetime.now().timestamp())

    result = set()
    for user, time in data:
        if time <= posix_time_now:
            result.add(int(user))
    return result


async def remove_timeout(timeout_ids, bot):
    guild_ids = await _get_guild_ids()
    for guild_id in guild_ids:
        unmute_candidates = await _fetch_candidates(guild_id)

        if not unmute_candidates:
            logger.info("No records fetched. Skipping cycle.")
            return

        guild = bot.get_guild(guild_id)
        timeout_roles = fetch_timeout_roles(guild)

        for candidate in unmute_candidates:
            member = await guild.fetch_member(candidate)
            if not timeout_ids.isdisjoint(set([str(role.id) for role in member.roles])):
                logger.info(f"Removed timeout for {member}")
                await member.remove_roles(*timeout_roles, reason="Timeout expired")
