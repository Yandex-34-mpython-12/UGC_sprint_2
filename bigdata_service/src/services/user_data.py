from uuid import UUID

from src.schemas.movie_rating import MovieRatingResponse
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import FilmRating
from sqlalchemy import select
from functools import lru_cache
from src.db.postgres import db_helper
from typing import Optional


class UserDataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_film_rating(self, user_id: UUID, movie_id: UUID, rating: int) -> MovieRatingResponse:
        query = select(FilmRating).where(FilmRating.user_id ==
                                         user_id, FilmRating.movie_id == movie_id)
        result = await self.db.execute(query)

        # Type hint for existing_rating should be Optional[FilmRating] since it can be None
        existing_rating: Optional[FilmRating] = result.scalars().first()

        if existing_rating:
            # If a rating exists, update it
            existing_rating.rating = rating
            await self.db.commit()
            await self.db.refresh(existing_rating)
            return MovieRatingResponse.from_orm(existing_rating)
        else:
            # If no rating exists, create a new one
            new_rating = FilmRating(
                user_id=user_id,
                movie_id=movie_id,
                rating=rating
            )
            self.db.add(new_rating)
            await self.db.commit()
            await self.db.refresh(new_rating)
            return MovieRatingResponse.from_orm(new_rating)


@lru_cache()
def get_user_data_service(
    db: AsyncSession = Depends(db_helper.session_getter),
) -> UserDataService:
    return UserDataService(db=db)
