from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field
from src.schemas.author import Author
from src.schemas.post import Like


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
    likes: list[Like] = Field(default_factory=list)

    class Settings:
        name = "posts"
        use_state_management = True
