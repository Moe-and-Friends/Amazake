import math
import logging

from .debounce import should_debounce

from ..config import config
from ..const import identifiers
from ..roles.roles import get_timeout_role

from api_extensions import guilds, members
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
        self.logger = logging.getLogger(__name__)
        self.unmute_loop.start()
        self.logger.info("Loaded Unmute cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.error(error)

    @tasks.loop(minutes=config.unmute_rate())
    async def unmute_loop(self):
        # TODO: Investigate if the unmute function can be executed within a transaction or a lock.
        # This is low-priority, since we assume each server only has one bot running for it.
        # discord.py can enqueue all loop events that failed, due to system sleep / etc.
        if should_debounce():
            self.logger.info("Skipping unmute loop due to debounce")
            return

        unmute_candidates = await self._fetch_unmute_candidates()
        if unmute_candidates:
            self.logger.info(f"Now processing unmute candidates: {unmute_candidates}")
            try:
                for candidate in unmute_candidates:
                    await self._remove_timeout_role(candidate)
                    self.logger.info(f"Finished processing candidate: {candidate}")
            except RuntimeError as e:
                # TODO: Specify a warning channel to send failures to.
                self.logger.critical(e)
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

        key = f"{identifiers.PACKAGE_KEY}_{config.guild()}"
        zrange_end = posix_time_now + timedelta(minutes=1)
        data = _redis_client.zrange(name=key,
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

    async def _remove_timeout_role(self, member_id: int):
        guild = await guilds.get_guild(config.guild(), self.bot)
        if not guild:
            raise RuntimeError(f"Guild {config.guild()} was not loaded. Please check your environment.")

        member = await members.get_member(member_id, guild)
        if not member:
            self.logger.warning(f"Member {member_id} could not be found. Not removing timeout role.")
            return

        role = await get_timeout_role(guild)
        try:
            # Note: If the role was already removed (e.g. by a moderator), this will simply not do anything.
            if role in member.roles:
                await member.remove_roles(role)
                self.logger.debug(f"Removed timeout role from user {member_id} ({member.name})")
            else:
                self.logger.info(
                    f"Member {member.id} ({member.name}) doesn't have the timeout role. It may have already been removed.")
        except Forbidden as e:
            self.logger.critical(f"Bot does not have sufficient permissions to remove the timeout role.")
            raise RuntimeError(e)
        except HTTPException as e:
            self.logger.critical(f"Unknown exception occurred when removing the timeout role. Please check your env.")
            raise RuntimeError(e)

        key = f"{identifiers.PACKAGE_KEY}_{config.guild()}"
        resp = _redis_client.zrem(key, str(member_id))
        # Even if the role was already removed, Redis still should be updated.
        if resp != 1:
            raise RuntimeError(f"{resp} members were removed from Redis, when 1 was expected!")

        return
