from dynaconf import Dynaconf, Validator
from typing import List, Optional

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
        Validator("bot_token", must_exist=True, is_type_of=str),
        # Roulette settings
        Validator("match_patterns", must_exist=True, is_type_of=list, len_min=1),
        Validator("channels", must_exist=True, is_type_of=list, len_min=1),
        Validator("protected", is_type_of=list),
        Validator("moderator", is_type_of=list),
        Validator("administrator", is_type_of=list),
        Validator("timeout_affected_messages_self", must_exist=True, is_type_of=list, len_min=1),
        Validator("timeout_affected_messages_other", must_exist=True, is_type_of=list, len_min=1),
        Validator("timeout_protected_messages_self", must_exist=True, is_type_of=list, len_min=1),
        Validator("timeout_protected_messages_other", must_exist=True, is_type_of=list, len_min=1),
        Validator("timeout_leaderboard_webhook_urls", is_type_of=list),
    ]
)


def bot_token() -> str:
    """
    :return: The bot token, as a string.
    """
    return _settings.get("bot_token")


def match_patterns() -> List[str]:
    return _settings.get("match_patterns")


def channels() -> List[str]:
    return _settings.get("channels")


def protected() -> Optional[List[str]]:
    return _settings.get("protected")


def moderator() -> Optional[List[str]]:
    return _settings.get("moderator")


def administrator() -> Optional[List[str]]:
    return _settings.get("administrator")


def timeout_affected_messages_self() -> List[str]:
    return _settings.get("timeout_affected_messages_self")


def timeout_affected_messages_other() -> List[str]:
    return _settings.get("timeout_affected_messages_other")


def timeout_protected_messages_self() -> List[str]:
    return _settings.get("timeout_protected_messages_self")


def timeout_protected_messages_other() -> List[str]:
    return _settings.get("timeout_protected_messages_other")


def timeout_leaderboard_webhook_urls() -> Optional[List[str]]:
    return _settings.get("timeout_leaderboard_webhook_urls")

# `envvar_prefix` = export envvars with `export ROULETTE_FOO=bar`.
# `settings_files` = Load these files in the order.
# `environments` = Export `ENV_FOR_DYNACONF=` to set an environment.
