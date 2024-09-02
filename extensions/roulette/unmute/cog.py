import logging

from . import action
from ..config import config
from ..config.redis_config import redis_client

from datetime import datetime
from discord import Role
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from typing import Set


class Unmute(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("roulette.unmute")
        self.unmute_loop.change_interval(minutes=config.unmute_rate())
        self.unmute_loop.start()
        self.logger.info("Loaded Unmute cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.warning(str(error))

    @tasks.loop(minutes=1)
    async def unmute_loop(self):
        await self._unmute(await self._get_guild_ids())

    async def _get_guild_ids(self) -> Set[int]:
        cursor = 0
        pattern = 'roulette_timeout_live*'

        guild_keys = set()
        guild_ids = set()

        while True:
            cursor, partial_keys = redis_client.scan(cursor=cursor, match=pattern)
            guild_keys.update(partial_keys)

            if cursor == 0:
                break

        for key in guild_keys:
            guild_ids.add(int(key[22:]))

        return guild_ids

    def _fetch_candidates(self, guild_id) -> Set[int]:
        key = f"roulette_timeout_live_{guild_id}"
        data = redis_client.zrange(key, start=0, end=-1, withscores=True)

        posix_time_now = int(datetime.now().timestamp())

        result = set()
        for user, time in data:
            if time <= posix_time_now:
                result.add(int(user))
        return result

    def _get_timeout_roles(self, guild) -> Set[Role]:
        role_ids_conf = config.timeout_roles()
        role_ids = set()

        for role_id_conf in role_ids_conf:
            role = guild.get_role(int(role_id_conf))
            if role:
                role_ids.add(role_id_conf)

        return {action.Role(role_id) for role_id in role_ids}

    async def _unmute(self, guild_ids):
        timeout_ids = set(config.timeout_roles())

        for guild_id in guild_ids:
            unmute_candidates = self._fetch_candidates(guild_id)

            if not unmute_candidates:
                self.logger.info("No records fetched. Skipping cycle.")
                return

            guild = self.bot.get_guild(guild_id)
            timeout_roles = self._get_timeout_roles(guild)

            for candidate in unmute_candidates:
                member = await guild.fetch_member(candidate)
                if not timeout_ids.isdisjoint(set([str(role.id) for role in member.roles])):
                    self.logger.info(f"Removed timeout from {member}")
                    await member.remove_roles(*timeout_roles, reason="Timeout expired")
