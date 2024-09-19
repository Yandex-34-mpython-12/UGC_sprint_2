import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import UUID4

from src.api.v1.deps import PaginationDep, QueryDep, SortDep
from src.models.auth import UserRole
from src.models.base import BaseOrjsonModel
from src.models.film import Film
from src.services.film import FilmService, get_film_service
from .auth import roles_required

router = APIRouter()

logger = logging.getLogger(__name__)


class FilmResponse(BaseOrjsonModel):
    uuid: UUID4
    title: str
    imdb_rating: float


@router.get('/', summary='Получение списка фильмов', response_model=list[FilmResponse])
@roles_required(roles_list=[UserRole.admin, UserRole.user])
async def get_films(
    request: Request,
    pagination_dep: PaginationDep,
    sort: SortDep,
    genre: UUID4 = Query(
        default=None,
        description='Жанр',
    ),
    film_service: FilmService = Depends(get_film_service),
):
    films = await film_service.get_films(
        url=str(request.url),
        genre=genre,
        page_number=pagination_dep['page_number'],
        page_size=pagination_dep['page_size'],
        sort=sort,
    )
    return films


@router.get('/search', summary='Поиск фильмов по названию', response_model=list[FilmResponse])
@roles_required(roles_list=[UserRole.admin, UserRole.user])
async def search_films_by_title(
    request: Request,
    pagination_dep: PaginationDep,
    sort: SortDep,
    query: QueryDep,
    film_service: FilmService = Depends(get_film_service),
):
    films = await film_service.get_films(
        url=str(request.url),
        query=query,
        page_number=pagination_dep['page_number'],
        page_size=pagination_dep['page_size'],
        sort=sort,
    )
    return films


@router.get('/{film_id}', summary='Информация о фильме по ID', response_model=Film)
@roles_required(roles_list=[UserRole.admin, UserRole.user])
async def film_details(film_id: UUID4, film_service: FilmService = Depends(get_film_service)):
    film = await film_service.get_film_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return film
