import logging
import requests

from ..config import config
from datetime import timedelta
from discord import Message

logger = logging.getLogger(__name__)


def timeout_record_stats(duration: timedelta, message: Message) -> None:
    """
    Records a timeout event for stats handling.
    :param duration: A timedelta representing the total duration of the timeout
    :param message: The original message that triggered the timeout
    """
    body = {
        "discord": {
            "user_id": str(message.author.id),
            "guild_id": str(message.guild.id)
        },
        "timeout": {
            "duration": int(duration / timedelta(minutes=1))
        }
    }

    for leaderboard_url in config.roll_timeout_leaderboard_webhook_urls():
        # Note: The IDs must be passed as strings to avoid auto-rounding.
        requests.post(leaderboard_url, json=body)
        logger.debug(f"Sending stats update to {leaderboard_url}")
