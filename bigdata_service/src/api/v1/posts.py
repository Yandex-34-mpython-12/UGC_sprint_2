import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from src.core.pagination import PaginatedPage
from src.models import Post
from src.schemas.post import Like, LikeCreateDto, PostCreateDto, PostResponse
from src.services.post import PostService, get_post_service

router = APIRouter(prefix='/posts', tags=['Posts'])

logger = logging.getLogger().getChild('posts-router')


@router.post(
    '',
    summary='Create a new post',
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
async def _create_post(
    dto: PostCreateDto,
    post_svc: PostService = Depends(get_post_service)
) -> Post:
    return await post_svc.create_post(dto=dto)


@router.get(
    '',
    summary='Get a list of posts',
    response_model=PaginatedPage[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _get_all_posts(
    post_svc: PostService = Depends(get_post_service)
) -> PaginatedPage[Post]:
    return await post_svc.get_all_posts()


@router.get('/{id}', response_model=PostResponse, status_code=status.HTTP_200_OK)
async def _get_post(
    id: UUID,
    bg_tasks: BackgroundTasks,
    post_svc: PostService = Depends(get_post_service),
) -> Post:
    post = await post_svc.get_by_id(post_id=id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found',
        )
    bg_tasks.add_task(post_svc.inc_post_view, post=post)
    return post


@router.delete('/{id}', summary='Delete post', status_code=status.HTTP_204_NO_CONTENT)
async def _delete_post(
    id: UUID,
    post_svc: PostService = Depends(get_post_service)
) -> None:
    post = await post_svc.get_by_id(post_id=id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with ID {id} not found',
        )
    await post_svc.delete_post(post=post)


@router.post(
    '/inc-views-proper',
    summary='Increase views for posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _increase_views(
    ids: list[UUID],
    post_svc: PostService = Depends(get_post_service),
) -> list[Post]:
    return await post_svc.inc_views(ids=ids)


@router.post(
    '/inc-views-transaction',
    summary='Increase views for posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _increase_views_transaction(
    ids: list[UUID],
    post_svc: PostService = Depends(get_post_service),
) -> list[Post]:
    return await post_svc.inc_views_transaction(ids=ids)


@router.get(
    '/author/{authors_last_name}',
    summary='Get all authors posts',
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def _get_authors_post(
    author_last_name: str,
    post_svc: PostService = Depends(get_post_service),
) -> list[Post]:
    return await post_svc.get_authors_post(author_last_name=author_last_name)


@router.get(
    '/statics/average-view',
    summary='Get average views',
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def _get_avg_views(post_svc: PostService = Depends(get_post_service)) -> dict:
    avg = await post_svc.get_avg_views()
    return {'result': avg}


@router.post(
    '/like',
    summary='Set like to post',
    response_model=Like,
    status_code=status.HTTP_201_CREATED,
)
async def _create_like(
    dto: LikeCreateDto,
    post_svc: PostService = Depends(get_post_service)
) -> Like:
    like = await post_svc.set_like(dto=dto)

    if like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {dto.post_id} not found',
        )

    return like
