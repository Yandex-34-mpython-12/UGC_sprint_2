from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.author import Author


class PostCreateDto(BaseModel):
    subject: str
    text: str
    author: Author


class Like(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: Author


class LikeCreateDto(BaseModel):
    post_id: UUID
    author: Author


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, populate_by_name=True)

    id: UUID = Field(UUID, validation_alias='_id')
    slug: str
    subject: str
    text: str
    is_published: bool
    views: int
    last_visit_at: datetime | None = None
    created_at: datetime
    author: Author
    likes: list[Like] | None = None
