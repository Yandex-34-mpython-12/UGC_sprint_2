from typing import Annotated

from fastapi import Depends, Query
from src.core.sort import FilmSortOptions


async def pagination_parameters(
    page_size: int = Query(
        default=10,
        ge=1,
        le=50,
        description='Количество фильмов на странице',
    ),
    page_number: int = Query(
        default=1,
        ge=1,
        description='Номер страницы',
    ),
):
    return {'page_size': page_size, 'page_number': page_number}


async def sort_param(
    sort: FilmSortOptions = Query(
        default=None,
        description='Сортировка',
    )
):
    return sort


async def query_param(
    query: str = Query(
        default=None,
        description='Поисковый запрос',
    )
):
    return query


PaginationDep = Annotated[dict, Depends(pagination_parameters)]
SortDep = Annotated[FilmSortOptions, Depends(sort_param)]
QueryDep = Annotated[str, Depends(query_param)]
