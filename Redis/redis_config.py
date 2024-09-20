import config
import redis

_pool = redis.ConnectionPool(
    host = config.redis_host(),
    port = config.redis_port()
)


def get_redis():
    redis_client = redis.Redis(
            connection_pool=_pool,
            password=config.redis_password(),
            username=config.redis_username()
    )
    return redis_client
