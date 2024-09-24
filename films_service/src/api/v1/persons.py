from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from src.api.v1.deps import PaginationDep, QueryDep
from src.api.v1.films import FilmResponse
from src.models.base import BaseOrjsonModel
from src.services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilms(BaseOrjsonModel):
    uuid: UUID4
    title: str
    imdb_rating: float | None = None
    role: str


class PersonResponse(BaseOrjsonModel):
    uuid: UUID4
    full_name: str
    films: list[PersonFilms]


@router.get('/search', summary='Поиск по персонам', response_model=list[PersonResponse])
async def search_persons(
    query: QueryDep,
    pagination_dep: PaginationDep,
    person_service: PersonService = Depends(get_person_service),
):
    persons = await person_service.get_persons(
        query=query,
        page_number=pagination_dep['page_number'],
        page_size=pagination_dep['page_size'],
    )
    return persons


@router.get('/{person_id}', summary='Информация о персонаже по ID', response_model=PersonResponse)
async def person_details(person_id: UUID4, person_service: PersonService = Depends(get_person_service)):
    person = await person_service.get_person_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return person


@router.get('/{person_id}/film', summary='Фильмы по персоне', response_model=list[FilmResponse])
async def person_films(person_id: UUID4, person_service: PersonService = Depends(get_person_service)):
    person = await person_service.get_person_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    films = person.films or []
    return films
