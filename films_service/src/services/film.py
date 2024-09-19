import logging
import uuid
from functools import lru_cache

from fastapi import Depends

from src.core.sort import FilmSortOptions
from src.db.elastic import get_elastic, AsyncElasticEngine
from src.db.redis import get_redis, AsyncRedisCache
from src.models.film import Film
from src.services.base_service import BaseService

FILMWORKS_INDEX = 'movies'
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5
logger = logging.getLogger(__name__)


class FilmService(BaseService):
    async def get_film_by_id(self, film_id: str) -> Film | None:
        film = await self._get_film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_search_db(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_cache(self, film_id: str) -> Film | None:
        cache_key = f'film:{film_id}'
        film = await self.get_from_cache(cache_key)
        if not film:
            return None
        return Film.model_validate_json(film)

    async def _get_film_from_search_db(self, film_id: str) -> Film | None:
        film = await self.get_by_id(index=FILMWORKS_INDEX, _id=film_id)
        if not film:
            return None
        return Film.parse_from_elastic(film)

    async def _put_film_to_cache(self, film: Film):
        cache_key = f'film:{film.uuid}'
        await self.set_to_cache(cache_key, film.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_films_from_cache(self, url: str) -> list[Film] | None:
        data = await self.get_from_cache(url)
        if not data:
            return None
        films = [Film.model_validate(film) for film in data]
        return films

    async def _put_films_to_cache(self, key: str, films: list[Film]):
        data = [film.model_dump_json() for film in films]
        await self.set_to_cache(key, data, FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_films_from_elastic(
        self,
        page_number: int,
        page_size: int,
        query: str | None = None,
        genre: uuid.UUID | None = None,
        sort: FilmSortOptions | None = None,
    ) -> list[Film]:
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
                        'fields': ['title'],
                        'fuzziness': 'AUTO',
                    }
                }
            )
        else:
            es_query['query']['bool']['must'].append({'match_all': {}})

        if genre:
            es_query['query']['bool']['must'].append(
                {'nested': {'path': 'genres', 'query': {
                    'term': {'genres.id': str(genre)}}}}
            )

        if sort:
            sort_key, sort_order = (sort.value[1:], 'desc') if sort.startswith(
                '-') else (sort.value, 'asc')
            es_query['sort'] = {sort_key: sort_order}

        documents = await self.search(index=FILMWORKS_INDEX, query=es_query)
        films = [Film.parse_from_elastic(doc) for doc in documents]
        return films

    async def get_films(
        self,
        url: str,
        page_number: int,
        page_size: int,
        query: str | None = None,
        genre: uuid.UUID | None = None,
        sort: FilmSortOptions | None = None,
    ) -> list[Film]:
        films = await self._get_films_from_cache(url)
        if not films:
            films = await self._get_films_from_elastic(
                query=query,
                genre=genre,
                page_number=page_number,
                page_size=page_size,
                sort=sort,
            )
            if not films:
                return []
            await self._put_films_to_cache(url, films)
        return films


@lru_cache()
def get_film_service(
    redis: AsyncRedisCache = Depends(get_redis),
    elastic: AsyncElasticEngine = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
