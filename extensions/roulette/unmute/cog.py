import math
import logging

from ..config import config

from database.redis_client import get_redis
from datetime import datetime, timedelta, timezone
from debounce import should_debounce
from discord.ext import tasks
from discord.ext.commands import Bot, Cog
from typing import Iterable

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

    @unmute_loop.before_loop
    async def before_unmute_loop(self):
        await self.bot.wait_until_ready()

    async def _fetch_unmute_candidates(self) -> Iterable[int]:
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

        self.logger.info(f"Unmute candidates: {candidates}")
        return candidates
