import redis.asyncio as redis
from src.config.settings import REDIS_URL

pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)


async def get_redis() -> redis.Redis:
    return redis.Redis(connection_pool=pool)
