from abc import ABC, abstractmethod
from typing import Any, Optional


class AsyncCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None, **kwargs) -> None:
        ...
