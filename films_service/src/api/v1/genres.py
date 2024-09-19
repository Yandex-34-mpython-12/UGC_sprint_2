from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import UUID4

from src.models.base import BaseOrjsonModel
from src.services.genre import GenreService, get_genre_service

router = APIRouter()


class GenreResponse(BaseOrjsonModel):
    uuid: UUID4
    name: str


@router.get('/', summary='Получение списка жанров', response_model=list[GenreResponse])
async def get_genres(request: Request, genre_service: GenreService = Depends(get_genre_service)):
    genres = await genre_service.get_genres(str(request.url))
    return genres


@router.get('/{genre_id}', summary='Информация о жанре по ID', response_model=GenreResponse)
async def get_genre_by_id(genre_id: UUID4, genre_service: GenreService = Depends(get_genre_service)):
    genre = await genre_service.get_genre_by_id(str(genre_id))
    if genre is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return genre
