import config
import redis

pool = redis.ConnectionPool(
    host = config.redis_host(),
    port = config.redis_port()
)

redis_client = redis.Redis(connection_pool=pool)
