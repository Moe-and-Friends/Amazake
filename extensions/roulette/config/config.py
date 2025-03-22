"""
Settings used by the Roulette extension.

Files under extensions/roll should always use configs defined here, not the
global-level config.
"""
import config as root_config
import re

from typing import Dict, Iterable, Optional, Tuple

_roulette_configuration = root_config.roulette_configuration()


def guild() -> str:
    """
    :return: The Discord Guild this bot is operating on.
    """
    if _roulette_configuration.HasField("guild"):
        return str(_roulette_configuration.guild)
    raise LookupError("No configuration provided for Roulette - Guild!")


def channels() -> Tuple[str]:
    """
    :return:  A list of channel IDs (as strings) representing channels that should be observed.
    """
    if len(channel_ids := tuple(str(c) for c in _roulette_configuration.channels)) > 0:
        return channel_ids
    raise LookupError("No channels to observe were provided for Roulette!")


def protected() -> Tuple[str]:
    """
    Roles that are immune to end-actions.
    :return: A list of role IDs (can be empty).
    """
    return tuple(str(r) for r in _roulette_configuration.protected_roles)


def moderator() -> Tuple[str]:
    """
    Roles that are able to run actions for other users.
    :return: A list of role IDs (can be empty).
    """
    return tuple(str(r) for r in _roulette_configuration.moderator_roles)


def administrator() -> Tuple[str]:
    """
    A reserved superuser role for future use.
    Administrators are implicitly moderators (and thus protected).
    :return: A list of user IDs.
    """
    if len(administrator_users := tuple(str(a) for a in _roulette_configuration.administrators)) > 0:
        return administrator_users
    raise LookupError("At least one administrator must be configured for Roulette!")


def unmute_rate() -> int:
    """
    :return: Time in minutes between each unmute loop, as an integer.
    """
    return root_config.roulette_unmute_rate() or 1


def timeout_role() -> Optional[str]:
    """
    A role that is applied to users to time them out.
    :return: A role ID, as a string.
    """
    return root_config.roulette_timeout_role() or None


def roll_match_patterns() -> Tuple[re.Pattern[str]]:
    """
    :return: A tuple of re.Pattern objects used to match messages for trigger hits.
    """
    # Explicitly type-cast here to prevent a warning.
    patterns: Iterable[str] = _roulette_configuration.patterns
    return tuple(re.compile(p) for p in patterns)


def roll_timeout_affected_messages_self() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for themselves.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.roulette_roll_timeout_affected_messages_self())


def roll_timeout_affected_messages_other() -> Tuple[str]:
    """
    A list of messages representing bot responses when a moderator or administrator rolls a mute for another user.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.roulette_roll_timeout_affected_messages_other())


def roll_timeout_protected_messages_self() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for themselves but is protected from the
        effect, such as a protected role, moderator, or administrator.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.roulette_roll_timeout_protected_messages_self())


def roll_timeout_protected_messages_other() -> Tuple[str]:
    """
    A list of messages representing bot responses when a user has rolled a mute for another user but that user is
        protected from the effect, e.g. having a protected role, moderator role, or being an administrator.
    Supported inline replacement values:
    - {timeout_user_name}: The display name of the user (will not be tagged)
    - {timeout_duration_label}: A display of the user's timeout duration
    """
    return tuple(str(m) for m in root_config.roulette_roll_timeout_protected_messages_other())


def roll_timeout_intervals() -> Tuple[Dict]:
    """
    A list of interval settings used to determine the gacha roll chances.
    Each interval is a dict, represented with the following keys:
    # Supported suffixes: m, h, d, w
    - bounds["lower"]: Lower bound (inclusive) of the roll value for this interval.
    - bounds["upper"]: Upper bound (inclusive) of the roll value for this interval.
    - weight: An integer indicating the non-cumulative weight (chance) for this interval.
    """
    # TODO: Maybe consider adding some kind of validation logic here.
    return tuple(root_config.roulette_roll_timeout_intervals())


def roll_timeout_response_delay_seconds() -> int:
    """
    :return: An upper bound delay between the roll and when the bot should respond, or 0 to disable.
    """
    return root_config.roulette_roll_timeout_response_delay_seconds() or 0


def roll_timeout_leaderboard_webhook_urls() -> Tuple[str]:
    """
    :return: A list of webhook URLs to send action events post-roll.
    """
    urls = root_config.roulette_roll_timeout_leaderboard_webhook_urls()
    return tuple(str(x) for x in urls) if urls else tuple()
