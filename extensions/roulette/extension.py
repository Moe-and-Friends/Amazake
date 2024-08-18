import logging

from discord.ext.commands import Bot
from .roulette.cog import Roulette

logger = logging.getLogger("roulette")


async def setup(bot: Bot) -> None:
    """
    Called by Discord.py to register this extension [directory].

    :param bot: The Discord bot the application is acting as
    """
    logger.info("Loading Roulette extension")
    await bot.add_cog(Roulette(bot))
