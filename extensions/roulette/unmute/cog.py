import math
import logging

from .debounce import should_debounce

from ..config import config
from ..roles.roles import get_timeout_role

from database.redis_client import get_redis
from datetime import datetime, timedelta, timezone
from discord import Forbidden, HTTPException
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from typing import List

_redis_client = get_redis()


class Unmute(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("roulette.unmute")
        self.unmute_loop.start()
        self.logger.info("Loaded Unmute cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.error(error)

    @tasks.loop(minutes=config.unmute_rate())
    async def unmute_loop(self):
        # TODO: Investigate if the unmute function can be executed within a transaction or a lock.
        # discord.py can enqueue all loop events that failed, due to system sleep / etc.
        if should_debounce():
            self.logger.info("Skipping unmute loop due to debounce")
            return

        unmute_candidates = await self._fetch_unmute_candidates()
        if unmute_candidates:
            self.logger.info(f"Now processing unmute candidates: {unmute_candidates}")
            for candidate in unmute_candidates:
                await self._remove_timeout_role(candidate)
        else:
            self.logger.debug("No unmute candidates for this loop.")

    @unmute_loop.before_loop
    async def before_unmute_loop(self):
        await self.bot.wait_until_ready()

    async def _fetch_unmute_candidates(self) -> List[int]:
        """
        :return: A list of users that should be unmuted. This can be empty if no users should be unmuted.
        """
        # Data is referenced in UTC time.
        posix_time_now = datetime.now(timezone.utc)

        zrange_end = posix_time_now + timedelta(minutes=1)
        data = _redis_client.zrange(name=config.guild(),
                                    start=0,
                                    # Must be an int, so cast up to avoid missing anyone.
                                    end=math.ceil(zrange_end.timestamp()),
                                    withscores=True)

        candidates = list()
        self.logger.debug(f"Current time: {posix_time_now.timestamp()} ({posix_time_now.strftime('%c')}) UTC")
        for user, time in data:
            # User is a bytestring
            user_id = user.decode("utf-8")

            self.logger.debug(
                f"User {user_id} has an unmute time of {time} ({datetime.fromtimestamp(time).strftime('%c')}) UTC")

            if time <= posix_time_now.timestamp():
                self.logger.debug(f"Added user {user_id} to unmute candidate queue.")
                candidates.append(int(user_id))

        self.logger.debug(f"Enqueue unmute candidates: {candidates}")
        return candidates

    async def _remove_timeout_role(self, user_id: int):
        guild = self.bot.get_guild(int(config.guild()))
        if not guild:
            self.logger.debug(f"Unable to get guild {config.guild()}, fetching via API")
            guild = await self.bot.fetch_guild(int(config.guild()))

        member = guild.get_member(user_id)
        if not member:
            self.logger.debug(f"Unable to get member {user_id}, fetching via API")
            member = await guild.fetch_member(user_id)

        role = await get_timeout_role(guild)
        try:
            await member.remove_roles(role)
            self.logger.debug(f"Removed timeout role from user {user_id} ({member.name})")
        except Forbidden:
            raise RuntimeError(f"Bot does not have sufficient permissions to remove the timeout role.")
        except HTTPException:
            raise RuntimeError(f"Unknown exception occurred when removing the timeout role. Please check your env.")

        resp = _redis_client.zrem(config.guild(), str(user_id))
        if resp != 1:
            raise RuntimeError(f"{resp} members were removed from Redis, when 1 was expected!")

        return
