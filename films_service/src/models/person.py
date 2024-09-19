from pydantic import Field

from src.models.base import BaseIdFullName, BaseOrjsonModel


class PersonFilms(BaseOrjsonModel):
    uuid: str
    title: str
    imdb_rating: float | None = None
    role: str


class Person(BaseOrjsonModel):
    uuid: str
    full_name: str
    films: list['PersonFilms'] = Field(default=list)

    @staticmethod
    def parse_from_elastic(document: dict) -> 'Person':
        return Person(
            uuid=document['_source']['id'],
            full_name=document['_source']['person'],
            films=[
                PersonFilms(uuid=film['id'], title=film['title'], imdb_rating=film['imdb_rating'], role=film['role'])
                for film in document['_source'].get('films', [])
            ],
        )


class Actor(BaseIdFullName):
    pass


class Writer(BaseIdFullName):
    pass


class Director(BaseIdFullName):
    pass
