import logging
from functools import lru_cache

from fastapi import Depends
from src.db.elastic import AsyncElasticEngine, get_elastic
from src.db.redis import AsyncRedisCache, get_redis
from src.models.person import Person
from src.services.base_service import BaseService

PERSONS_INDEX = 'persons'
PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5
logger = logging.getLogger(__name__)


class PersonService(BaseService):
    async def get_persons(
        self,
        page_number: int,
        page_size: int,
        query: str | None = None,
    ) -> list[Person]:
        es_query = {
            'query': {'bool': {'must': []}},
            'size': page_size,
            'from': (page_number - 1) * page_size,
        }
        if query:
            es_query['query']['bool']['must'].append(
                {
                    'multi_match': {
                        'query': query,
                        'fields': ['person'],
                        'fuzziness': 'AUTO',
                    }
                }
            )
        else:
            es_query['query']['bool']['must'].append({'match_all': {}})
        documents = await self.search(index=PERSONS_INDEX, query=es_query)
        persons = [Person.parse_from_elastic(doc) for doc in documents]
        return persons

    async def get_person_by_id(self, person_id: str) -> Person | None:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_search_db(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_search_db(self, person_id: str) -> Person | None:
        person = await self.get_by_id(index=PERSONS_INDEX, _id=person_id)
        if not person:
            return None
        return Person.parse_from_elastic(person)

    async def _person_from_cache(self, person_id: str) -> Person | None:
        cache_key = f'person:{person_id}'
        person = await self.get_from_cache(cache_key)
        if not person:
            return None
        return Person.model_validate_json(person)

    async def _put_person_to_cache(self, person: Person):
        cache_key = f'person:{person.uuid}'
        await self.set_to_cache(cache_key, person.model_dump_json(), PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    elastic: AsyncElasticEngine = Depends(get_elastic),
    redis: AsyncRedisCache = Depends(get_redis),
) -> PersonService:
    return PersonService(redis, elastic)
