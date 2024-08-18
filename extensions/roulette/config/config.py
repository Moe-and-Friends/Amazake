"""
Settings used by the Roulette extension.

Files under extensions/roulette should always use configs defined here, not the
global-level config.
"""
import config as root_config
import re

from typing import Tuple


def match_patterns() -> Tuple[re.Pattern[str]]:
    """
    :return: A tuple of re.Pattern objects used to match messages for trigger hits.
    """
    return tuple(re.compile(r) for r in root_config.match_patterns())


def channels() -> Tuple[str]:
    """
    :return:  A list of channel IDs (as strings) representing channels that should be observed.
    """
    return tuple(str(c) for c in root_config.channels())


def protected() -> Tuple[str]:
    """
    Roles that are immune to end-actions.
    :return: A list of role IDs.
    """
    # Default to an empty list of
    roles = root_config.protected()
    return tuple(str(r) for r in roles) if roles else tuple()


def moderator() -> Tuple[str]:
    """
    Roles that are able to run actions for other users.
    Moderator roles are also implicitly protected roles.
    :return: A list of role IDs.
    """
    roles = root_config.moderator()
    return tuple(str(r) for r in roles) if roles else tuple()


def administrator() -> Tuple[str]:
    """
    A reserved superuser role for future use.
    Administrators are implicitly moderators (and thus protected).
    :return: A list of user IDs.
    """
    users = root_config.administrator()
    return tuple(str(u) for u in users) if users else tuple()


def leaderboard_webhook_urls() -> Tuple[str]:
    """
    :return: A list of webhook URLs to send action events post-roll.
    """
    urls = root_config.timeout_leaderboard_webhook_urls()
    return tuple(str(x) for x in urls) if urls else tuple()