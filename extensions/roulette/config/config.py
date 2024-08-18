"""
Settings used by the Roulette extension.

Files under extensions/roulette should always use configs defined here, not the
global-level config.
"""
import config as root_config
import re

from typing import Dict, Tuple


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


def timeout_affected_messages_self() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for themselves.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.timeout_affected_messages_self())


def timeout_affected_messages_other() -> Tuple[str]:
    """
    A list of messages representing bot responses when a moderator or administrator rolls a mute for another user.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.timeout_affected_messages_other())


def timeout_protected_messages_self() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for themselves but is protected from the
        effect, such as a protected role, moderator, or administrator.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.timeout_protected_messages_self())


def timeout_protected_messages_other() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for another user but that user is
        protected from the effect, e.g. having a protected role, moderator role, or being an administrator.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.timeout_protected_messages_other())


def roll_intervals() -> Tuple[Dict]:
    """
    A list of interval settings used to determine the gacha roll chances.
    Each interval is a dict, represented with the following keys:
    # Supported suffixes: m, h, d, w
    - bounds["lower"]: Lower bound (inclusive) of the roll value for this interval.
    - bounds["upper"]: Upper bound (inclusive) of the roll value for this interval.
    - weight: An integer indicating the non-cumulative weight (chance) for this interval.
    """
    # TODO: Maybe consider adding some kind of validation logic here.
    return tuple(root_config.timeout_intervals())


def leaderboard_webhook_urls() -> Tuple[str]:
    """
    :return: A list of webhook URLs to send action events post-roll.
    """
    urls = root_config.timeout_leaderboard_webhook_urls()
    return tuple(str(x) for x in urls) if urls else tuple()
