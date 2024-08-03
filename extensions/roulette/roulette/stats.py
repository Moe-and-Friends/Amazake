import logging
import requests

from config import settings
from datetime import timedelta
from discord import Message

logger = logging.getLogger("roulette")


def timeout_record_stats(duration: timedelta, message: Message) -> None:
    """
    Records a timeout event for stats handling. Sends a request with the following JSON form:
    {
        "discord": {
            "user_id": <author's id: str>, <-- This means moderators are attributed for rolls even on other users.
            "guild_id": <guild_id: str>
        },
        "timeout": {
            "duration": <duration of the timeout: int>
        }
    }
    :param duration: A timedelta representing the total duration of the timeout
    :param message: The original message that triggered the timeout
    """
    leaderboard_url = settings.get("timeout_leaderboard_url")
    if not leaderboard_url:
        logger.debug("No timeout leaderboard URL detected, not sending stats")
        return

    # Note: The IDs must be passed as strings to avoid auto-rounding.
    requests.post(leaderboard_url, json={
        "discord": {
            "user_id": str(message.author.id),
            "guild_id": str(message.guild.id)
        },
        "timeout": {
            "duration": int(duration / timedelta(minutes=1))
        }
    })
    logger.debug(f"Sending stats update to {leaderboard_url}")
