from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from src.core.search_engine import AsyncSearchEngine

es: AsyncElasticsearch | None = None


async def get_elastic() -> 'AsyncElasticEngine':
    return AsyncElasticEngine(es)


class AsyncElasticEngine(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.es = elastic

    async def get_by_id(self, index: str, _id: str) -> Any | None:
        try:
            doc = await self.es.get(index=index, id=_id)
        except NotFoundError:
            return None
        return doc

    async def search(self, index: str, body: dict) -> Any | None:
        try:
            data = await self.es.search(index=index, body=body)
        except NotFoundError:
            return []

        return data['hits']['hits']
