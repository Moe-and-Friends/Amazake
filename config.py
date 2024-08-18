from dynaconf import Dynaconf, Validator
from typing import Dict, List, Optional

_settings = Dynaconf(
    envvar_prefix="ROULETTE",
    environments=True,
    load_dotenv=True,
    settings_files=[
        'settings.toml',
        '.secrets.toml',
        'settings.yml',
        '.secrets.yml'
    ],
    validators=[
        # Bot settings
        Validator("log_level", is_type_of=str),
        Validator("bot_token", must_exist=True, is_type_of=str),
        # Roulette settings
        Validator("roulette_channels", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_protected_roles", is_type_of=list),
        Validator("roulette_moderator_roles", is_type_of=list),
        Validator("roulette_administrator_users", is_type_of=list),
        Validator("roulette_roll_match_patterns", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_roll_timeout_affected_messages_self", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_roll_timeout_affected_messages_other", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_roll_timeout_protected_messages_self", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_roll_timeout_protected_messages_other", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_roll_timeout_leaderboard_webhook_urls", is_type_of=list),
        Validator("roulette_roll_timeout_response_delay_seconds", is_type_of=int),
        Validator("roulette_roll_timeout_intervals", must_exist=True, is_type_of=list)
    ]
)


def log_level() -> str:
    """
    :return: The logging level that should be used for this application. Does not affect Discord.py logging.
    """
    return str(_settings.get("log_level", "INFO")).upper()


def bot_token() -> str:
    """
    :return: The bot token, as a string.
    """
    return _settings.get("bot_token")


def roulette_roll_match_patterns() -> List[str]:
    return _settings.get("roulette_roll_match_patterns")


def roulette_channels() -> List[str]:
    return _settings.get("roulette_channels")


def roulette_protected_roles() -> Optional[List[str]]:
    return _settings.get("roulette_protected_roles")


def roulette_moderator_roles() -> Optional[List[str]]:
    return _settings.get("roulette_moderator_roles")


def roulette_administrator_users() -> Optional[List[str]]:
    return _settings.get("roulette_administrator_users")


def roulette_roll_timeout_affected_messages_self() -> List[str]:
    return _settings.get("roulette_roll_timeout_affected_messages_self")


def roulette_roll_timeout_affected_messages_other() -> List[str]:
    return _settings.get("roulette_roll_timeout_affected_messages_other")


def roulette_roll_timeout_protected_messages_self() -> List[str]:
    return _settings.get("roulette_roll_timeout_protected_messages_self")


def roulette_roll_timeout_protected_messages_other() -> List[str]:
    return _settings.get("roulette_roll_timeout_protected_messages_other")


def roulette_roll_timeout_leaderboard_webhook_urls() -> Optional[List[str]]:
    return _settings.get("roulette_roll_timeout_leaderboard_webhook_urls")


def roulette_roll_timeout_response_delay_seconds() -> Optional[int]:
    return _settings.get("roulette_roll_timeout_response_delay_seconds")


def roulette_roll_timeout_intervals() -> List[Dict]:
    return _settings.get("roulette_roll_timeout_intervals")

# `envvar_prefix` = export envvars with `export ROULETTE_FOO=bar`.
# `settings_files` = Load these files in the order.
# `environments` = Export `ENV_FOR_DYNACONF=` to set an environment.
