import os

from dynaconf import Dynaconf, Validator
from google.protobuf import text_format
from settings import app_config_pb2
from typing import Dict, List, Optional

_ENV_VAR_PREFIX = "AMAZAKE"

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
        # Roulette settings
        Validator("roulette_guild", must_exist=True, is_type_of=str),
        Validator("roulette_channels", must_exist=True, is_type_of=list, len_min=1),
        Validator("roulette_timeout_role", must_exist=True, is_type_of=str),
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
        Validator("roulette_roll_timeout_intervals", must_exist=True, is_type_of=list),
        Validator("roulette_unmute_rate", is_type_of=int),
    ]
)

with open("settings/app_config.textproto", "r") as f:
    _settings_proto = text_format.Parse(f.read(), app_config_pb2.AppConfiguration())
    print(_settings_proto)


def log_level() -> str:
    """
    :return: The logging level that should be used for this application. Does not affect Discord.py logging.
    """
    if (env_log_level := os.getenv(f"{_ENV_VAR_PREFIX}_LOG_LEVEL")) is not None:
        return env_log_level
    if _settings_proto.HasField("log_level"):
        return _settings.log_level
    raise LookupError("No configuration was found for logging level!")


def bot_token() -> str:
    """
    :return: The bot token, as a string.
    """
    if (env_token := os.getenv(f"{_ENV_VAR_PREFIX}_BOT_TOKEN")) is not None:
        return env_token
    if _settings_proto.HasField("bot_token"):
        return _settings.bot_token
    raise LookupError("No configuration was found for the bot token!")


def redis_configuration() -> app_config_pb2.AppConfiguration.RedisConfiguration:
    # Okay to return the default value.
    return _settings_proto.redis_configuration


def redis_key_const() -> Optional[str]:
    return _settings.get("redis_key_const") or None


def roulette_roll_match_patterns() -> List[str]:
    return _settings.get("roulette_roll_match_patterns")


def roulette_guild() -> str:
    return _settings.get("roulette_guild")


def roulette_channels() -> List[str]:
    return _settings.get("roulette_channels")


def roulette_timeout_role() -> Optional[str]:
    return _settings.get("roulette_timeout_role")


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


def roulette_unmute_rate() -> Optional[int]:
    return _settings.get("roulette_unmute_rate") or None

# `envvar_prefix` = export envvars with `export ROULETTE_FOO=bar`.
# `settings_files` = Load these files in the order.
# `environments` = Export `ENV_FOR_DYNACONF=` to set an environment.
