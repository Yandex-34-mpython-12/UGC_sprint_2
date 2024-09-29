from datetime import datetime, timezone
from functools import lru_cache
from uuid import UUID

from beanie.odm.operators.find.comparison import In
from fastapi import Depends
from fastapi_pagination import paginate
from motor.motor_asyncio import AsyncIOMotorClient
from slugify import slugify
from src.db.mongo import get_mongo_client
from src.models import Post
from src.schemas.post import Like, LikeCreateDto, PostCreateDto


class PostService:
    def __init__(self, *, mongo_client: AsyncIOMotorClient) -> None:
        self.mongo_client = mongo_client

    @classmethod
    async def create_post(cls, *, dto: PostCreateDto) -> Post:
        post = await Post(
            slug=slugify(dto.subject),
            subject=dto.subject,
            text=dto.text,
            author=dto.author,
        ).insert()
        return post

    @classmethod
    async def get_all_posts(cls) -> list[Post]:
        items = await paginate(Post.find_all())
        return items

    @classmethod
    async def get_by_id(cls, *, post_id: UUID) -> Post | None:
        return await Post.find_one(Post.id == post_id)

    @classmethod
    async def inc_post_view(cls, *, post: Post) -> None:
        await Post.find_one(Post.id == post.id).update(
            {"$inc": {"views": 1}, "$set": {"last_visit_at": datetime.now(timezone.utc)}}
        )

    @classmethod
    async def delete_post(cls, *, post: Post) -> None:
        await post.delete()

    @classmethod
    async def inc_views(cls, *, ids: list[UUID]) -> list[Post]:
        query = Post.find(In(Post.id, ids))
        await query.inc({Post.views: 1})
        return await query.to_list()

    async def inc_views_transaction(self, *, ids: list[UUID]) -> list[Post]:
        posts = []
        async with await self.mongo_client.start_session() as session:
            async with session.start_transaction():
                for _id in ids:
                    post = await Post.find_one(Post.id == _id, session=session)
                    if not post:
                        continue
                    post.views += 1
                    await post.replace(session=session)
                    posts.append(post)
        return posts

    @classmethod
    async def get_authors_post(cls, *, author_last_name: str) -> list[Post]:
        return await Post.find_many(Post.author.last_name == author_last_name).to_list()

    @classmethod
    async def get_avg_views(cls) -> float:
        return await Post.find().avg(Post.views)

    @classmethod
    async def get_by_slug(cls, *, slug: str) -> Post:
        return await Post.find_one(Post.slug == slug)

    @classmethod
    async def set_like(cls, *, dto: LikeCreateDto) -> Like | None:
        like = Like(author=dto.author)
        result = await Post.find_one(Post.id == dto.post_id).update({"$push": {"likes": like}})
        if result.modified_count == 0:
            return None

        return like


@lru_cache()
def get_post_service(mongo_client=Depends(get_mongo_client)) -> PostService:
    return PostService(mongo_client=mongo_client)
