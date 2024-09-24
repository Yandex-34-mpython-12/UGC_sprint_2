from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


class FilmRating(Base):
    __tablename__ = 'movie_ratings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    movie_id = Column(UUID(as_uuid=True), nullable=False)
    rating = Column(Integer, nullable=False)
