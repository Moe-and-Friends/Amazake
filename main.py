import sys

import config
import discord
import logging

from discord.ext.commands import Bot


intents = discord.Intents.default()
intents.message_content = True

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("roulette")
handler = logging.StreamHandler(stream=sys.stderr)

bot = Bot(command_prefix="roll", intents=intents)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await bot.load_extension("extensions.roulette.extension")

if __name__ == '__main__':
    bot.run(config.bot_token(), log_handler=handler, log_level=logging.INFO)
