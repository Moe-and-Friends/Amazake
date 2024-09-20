import logging

from ..config import config
from ..database.redis_db import remove_timeout

from discord.ext import tasks
from discord.ext.commands import Bot, Cog


class Unmute(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("roulette.unmute")
        self.unmute_loop.change_interval(minutes=config.unmute_rate())
        self.unmute_loop.start()
        self.logger.info("Loaded Unmute cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.error(str(error))

    @tasks.loop(minutes=1)
    async def unmute_loop(self):
        timeout_ids = set(config.timeout_roles())
        await remove_timeout(timeout_ids, self.bot)
