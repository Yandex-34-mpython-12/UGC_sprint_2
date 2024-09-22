from src.models.base import BaseOrjsonModel
from src.models.genre import Genre
from src.models.person import Actor, Director, Writer


class Film(BaseOrjsonModel):
    uuid: str
    title: str
    description: str | None = None
    imdb_rating: float | None = None
    actors: list[Actor] | None = None
    writers: list[Writer] | None = None
    directors: list[Director] | None = None
    genres: list[Genre] | None = None

    @staticmethod
    def parse_from_elastic(document: dict) -> 'Film':
        return Film(
            uuid=document['_source']['id'],
            title=document['_source']['title'],
            description=document['_source']['description'],
            imdb_rating=document['_source']['imdb_rating'],
            actors=[
                Actor(
                    uuid=person['id'],
                    full_name=person['name'],
                )
                for person in document['_source']['actors']
            ],
            writers=[
                Writer(
                    uuid=person['id'],
                    full_name=person['name'],
                )
                for person in document['_source']['writers']
            ],
            directors=[
                Director(
                    uuid=person['id'],
                    full_name=person['name'],
                )
                for person in document['_source']['writers']
            ],
            genres=[Genre(uuid=genre['id'], name=genre['name'])
                    for genre in document['_source']['genres']],
        )
