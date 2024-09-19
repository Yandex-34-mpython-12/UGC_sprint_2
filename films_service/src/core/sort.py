from enum import Enum


class FilmSortOptions(str, Enum):
    asc = 'imdb_rating'
    desc = '-imdb_rating'
