import logging
from uuid import UUID

from beanie.odm.operators.find.comparison import In
from fastapi import APIRouter, status, HTTPException, BackgroundTasks
from fastapi_pagination.ext.beanie import paginate

from src.core.config import settings
from src.core.pagination import PaginatedPage
from src.db import mongo
from src.models import Post
from src.schemas.post import PostResponse, PostCreateDto, Like, LikeCreateDto

router = APIRouter(prefix='/posts', tags=['Posts'])

logger = logging.getLogger().getChild('posts-router')


@router.post(
    '',
    summary='Create a new post',
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
async def _create_post(dto: PostCreateDto) -> Post:
    post = await Post.create_new(dto=dto)
    return post


@router.get(
    '',
    summary='Get a list of posts',
    response_model=PaginatedPage[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _get_all_posts() -> PaginatedPage[Post]:
    items = await paginate(Post.find_all())
    return items


@router.get(
    '/raw-list/',
    summary='Get a list of posts without ODM',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _get_items(page: int = 1, limit: int = 10) -> list[Post]:
    client = mongo.mongo_client[settings.mongo.mongodb_db_name]
    return await client.posts.find().skip(page).limit(limit).to_list(limit)


@router.get('/{id}', response_model=PostResponse, status_code=status.HTTP_200_OK)
async def _get_post(id: UUID, bg_tasks: BackgroundTasks) -> Post:
    post = await Post.get_by_id(id=id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found',
        )
    bg_tasks.add_task(Post.visit, instance=post)
    return post


@router.delete('/{id}', summary='Delete post', status_code=status.HTTP_204_NO_CONTENT)
async def _delete_post(id: UUID) -> None:
    post = await Post.get_by_id(id=id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with ID {id} not found',
        )
    await post.delete()


@router.post(
    '/inc-views-proper',
    summary='Increase views for posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _increase_views(ids: list[UUID]) -> list[Post]:
    query = Post.find(In(Post.id, ids))
    await query.inc({Post.views: 1})
    return await query.to_list()


@router.post(
    '/inc-views-transaction',
    summary='Increase views for posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _increase_views_transaction(ids: list[UUID]) -> list[Post]:
    posts = []
    """
        Wrong way:
        for id in ids:
        post = await Post.find_one(Post.id == id)
        post.views += 1
        await post.replace()
        posts.append(post)
    """
    async with await mongo.mongo_client.start_session() as session:
        async with session.start_transaction():
            for id in ids:
                post = await Post.find_one(Post.id == id, session=session)
                post.views += 1
                await post.replace(session=session)
                posts.append(post)
    return posts


@router.get(
    '/author/{authors_last_name}',
    summary='Get all authors posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _get_authors_post(authors_last_name: str) -> list[Post]:
    return await Post.find_many(Post.author.last_name == authors_last_name).to_list()


@router.get(
    '/statics/average-view',
    summary='Get average views',
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def _get_avg_views() -> dict:
    avg = await Post.find().avg(Post.views)
    return {'result': avg}


@router.post(
    '/like',
    summary='Set like to post',
    response_model=Like,
    status_code=status.HTTP_201_CREATED,
)
async def _create_like(dto: LikeCreateDto) -> Like:
    post = await Post.get_by_id(id=dto.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found',
        )
    like = Like(author=dto.author)
    post.likes.append(like)
    await post.replace()

    return like
