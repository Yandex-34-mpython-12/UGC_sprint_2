from uuid import UUID

from pydantic import BaseModel, Field


class MovieRatingCreate(BaseModel):
    movie_id: UUID
    rating: int = Field(..., ge=1, le=5)


class MovieRatingResponse(BaseModel):
    id: int
    user_id: UUID
    movie_id: UUID
    rating: int

    class Config:
        from_attributes = True
