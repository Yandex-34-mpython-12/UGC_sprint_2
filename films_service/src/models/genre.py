from src.models.base import BaseOrjsonModel


class Genre(BaseOrjsonModel):

    uuid: str
    name: str

    @staticmethod
    def parse_from_elastic(document: dict) -> 'Genre':
        return Genre(
            uuid=document['_source']['id'],
            name=document['_source']['genre'],
        )
