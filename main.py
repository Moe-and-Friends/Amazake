import config
import discord
import logging

from colorlog import ColoredFormatter
from discord.ext.commands import Bot


intents = discord.Intents.default()
intents.message_content = True

formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'white',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={},
    style='%'
)

# Configure the root logger so all loggers have the same general output.
stream = logging.StreamHandler()
stream.setFormatter(formatter)
logging.root.addHandler(stream)
logging.root.setLevel(config.log_level())

logger = logging.getLogger(__name__)

bot = Bot(command_prefix="roll", intents=intents)


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await bot.load_extension("extensions.roulette.extension")

if __name__ == '__main__':
    # Note: Discord.py configures its own logger [prior to the root logger] - keep this at INFO.
    bot.run(config.bot_token(), log_handler=stream, log_level=logging.INFO)
