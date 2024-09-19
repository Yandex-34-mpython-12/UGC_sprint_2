from abc import ABC, abstractmethod
from typing import Any


class AsyncSearchEngine(ABC):
    @abstractmethod
    async def get_by_id(self, index: str, _id: str) -> Any | None:
        ...

    @abstractmethod
    async def search(self, index: str, body: dict) -> Any | None:
        ...
