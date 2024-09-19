from abc import ABC, abstractmethod
from typing import Any


class AsyncCache(ABC):
    def __init__(self, cache: Any):
        self._cache = cache

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int | None, **kwargs) -> None:
        pass

    @property
    def cache(self) -> Any:
        return self._cache

    @cache.setter
    def cache(self, value: Any) -> None:
        self._cache = value
