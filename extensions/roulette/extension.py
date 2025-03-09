import logging

from discord.ext.commands import Bot
from .roll.cog import Roll
from .unmute.cog import Unmute

logger = logging.getLogger("roulette")


async def setup(bot: Bot) -> None:
    """
    Called by Discord.py to register this extension [directory].

    :param bot: The Discord bot the application is acting as
    """

    # TODO: Re-enable Redis-based mutes.
    logger.info("Loading Unmute extension")
    await bot.add_cog(Unmute(bot))
    logger.info("Loaded Unmute extension")

    # logger.info("Loading Roll extension")
    # await bot.add_cog(Roll(bot))
    # logger.info("Loaded Roll extension")
