from datetime import datetime, timezone
from typing import Self
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field
from slugify import slugify

from src.schemas.author import Author
from src.schemas.post import PostCreateDto


class Post(Document):
    id: UUID = Field(default_factory=uuid4)
    slug: Indexed(str, unique=False)
    subject: Indexed(str, unique=False)
    text: str
    is_published: bool = True
    views: int = 0
    last_visit_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    author: Author

    @classmethod
    async def create_new(
        cls,
        *,
        dto: PostCreateDto,
    ) -> Self:
        return await cls(
            slug=slugify(dto.subject),
            subject=dto.subject,
            text=dto.text,
            author=dto.author,
        ).insert()

    @classmethod
    async def get_by_slug(cls, *, slug: str) -> Self:
        return await cls.find_one(cls.slug == slug)

    @classmethod
    async def get_by_id(cls, *, id: UUID) -> Self:
        return await cls.find_one(cls.id == id)

    @classmethod
    async def visit(cls, *, instance: Self) -> None:
        await cls.find_one(cls.id == instance.id).update(
            {"$inc": {"views": 1}, "$set": {"last_visit_at": datetime.now(timezone.utc)}}
        )

    class Settings:
        name = 'posts'
        use_state_management = True
