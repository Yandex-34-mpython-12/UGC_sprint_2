import logging
from functools import lru_cache

from fastapi import Depends

from src.db.elastic import get_elastic, AsyncElasticEngine
from src.db.redis import get_redis, AsyncRedisCache
from src.models.genre import Genre
from src.services.base_service import BaseService

GENRES_INDEX = 'genres'
GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5
logger = logging.getLogger(__name__)


class GenreService(BaseService):
    async def get_genres(self, url: str) -> list[Genre]:
        genres = await self._get_genres_from_cache(url)
        if not genres:
            genres = await self._get_genres_from_elastic()
            if not genres:
                return []
            await self._put_genres_to_cache(url, genres)
        return genres

    async def get_genre_by_id(self, genre_id: str) -> Genre | None:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Genre | None:
        genre = await self.get_by_id(index=GENRES_INDEX, _id=genre_id)
        if not genre:
            return None
        return Genre.parse_from_elastic(genre)

    async def _get_genres_from_elastic(self):
        es_query = {'query': {'bool': {'must': {'match_all': {}}}}}
        documents = await self.search(index=GENRES_INDEX, query=es_query)
        genres = [Genre.parse_from_elastic(doc) for doc in documents]
        return genres

    async def _genre_from_cache(self, genre_id: str) -> Genre | None:
        cache_key = f'genre:{genre_id}'
        genre = await self.get_from_cache(cache_key)
        if not genre:
            return None
        return Genre.model_validate_json(genre)

    async def _put_genre_to_cache(self, genre: Genre):
        cache_key = f'genre:{genre.uuid}'
        await self.set_to_cache(cache_key, genre.model_dump_json(), GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def _get_genres_from_cache(self, url: str) -> list[Genre] | None:
        data = await self.get_from_cache(url)
        if not data:
            return None
        genres = [Genre.model_validate(genre) for genre in data]
        return genres

    async def _put_genres_to_cache(self, key: str, genres: list[Genre]):
        data = [genre.model_dump_json() for genre in genres]
        await self.set_to_cache(key, data, GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
    elastic: AsyncElasticEngine = Depends(get_elastic), redis: AsyncRedisCache = Depends(get_redis)
) -> GenreService:
    return GenreService(redis, elastic)
