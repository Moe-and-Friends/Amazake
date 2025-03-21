import config as root_config
import os

from typing import Optional

_redis_configuration = root_config.redis_configuration()

_ENV_VAR_PREFIX = "AMAZAKE_REDIS"


def host() -> str:
    """
    :return: The Redis host.
    """
    if (env_host := os.getenv(f"{_ENV_VAR_PREFIX}_HOST")) is not None:
        return env_host
    if _redis_configuration.HasField("host"):
        return _redis_configuration.host
    return "localhost"


def port() -> int:
    """
    :return: The Redis port.
    """
    if (env_port := os.getenv(f"{_ENV_VAR_PREFIX}_PORT")) is not None:
        return int(env_port)
    if _redis_configuration.HasField("port"):
        return _redis_configuration.port
    return 6379


def username() -> Optional[str]:
    """
    :return: A username to log into Redis with, or none if not applicable.
    """
    if (env_username := os.getenv(f"{_ENV_VAR_PREFIX}_USERNAME")) is not None:
        return env_username
    if _redis_configuration.HasField("username"):
        return _redis_configuration.username
    return None


def password() -> Optional[str]:
    """
    :return: A password to log into Redis with, or none if not applicable.
    """
    if (env_password := os.getenv(f"{_ENV_VAR_PREFIX}_PASSWORD")) is not None:
        return env_password
    if _redis_configuration.HasField("password"):
        return _redis_configuration.password
    return None
