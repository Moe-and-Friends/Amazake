import logging

from discord.ext.commands import Bot
from .roll.cog import Roll

logger = logging.getLogger("roulette")


async def setup(bot: Bot) -> None:
    """
    Called by Discord.py to register this extension [directory].

    :param bot: The Discord bot the application is acting as
    """
    logger.info("Loading Roll extension")
    await bot.add_cog(Roll(bot))
    logger.info("Loaded Roll extension")
