import redis

from . import redis_config

_pool = redis.ConnectionPool(
    host=redis_config.host(),
    port=redis_config.port()
)


def get_redis():
    """
    :return: A shared Redis Client that is thread-safe and can be used across Cogs.
    """
    redis_client = redis.Redis(
        connection_pool=_pool,
        username=redis_config.username(),
        password=redis_config.password()
    )
    return redis_client
