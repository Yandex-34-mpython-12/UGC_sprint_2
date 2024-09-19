from abc import ABC
from typing import Any

from src.core.cache import AsyncCache
from src.core.search_engine import AsyncSearchEngine


class BaseService(ABC):
    def __init__(self, cache: AsyncCache, search_engine: AsyncSearchEngine):
        self.cache = cache
        self.search_engine = search_engine

    async def get_by_id(self, index: str, _id: str) -> Any | None:
        obj = await self.search_engine.get_by_id(index, _id)
        return obj

    async def search(self, index: str, query: dict):
        data = await self.search_engine.search(
            index=index,
            body=query,
        )

        return data

    async def get_from_cache(self, key: str) -> Any | None:
        data = await self.cache.get(key)
        return data

    async def set_to_cache(self, key: str, value: Any, expire: int | None, **kwargs):
        await self.cache.set(key, value, expire, **kwargs)
