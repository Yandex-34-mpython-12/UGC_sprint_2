from typing import Any, Optional

from redis.asyncio import Redis
from src.db.base_cache import AsyncCache

redis: Optional[Redis] = None


def get_redis() -> "AsyncRedisCache":
    return AsyncRedisCache(redis)


class AsyncRedisCache(AsyncCache):
    def __init__(self, redis_cache: Redis):
        self.redis = redis_cache

    async def get(self, key: str) -> Any | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None, **kwargs) -> None:
        await self.redis.set(key, value, expire, **kwargs)
