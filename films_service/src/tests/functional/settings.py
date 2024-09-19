from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='tests.env', env_file_encoding='utf-8', extra='ignore')

    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    elastic_host: str = Field('127.0.0.1', alias='ELASTICSEARCH_HOST')
    elastic_port: int = Field(9200, alias='ELASTICSEARCH_PORT')
    elastic_schema: str = Field('http', alias='ELASTICSEARCH_SCHEMA')
    elastic_films_index: str = Field('movies', alias='ELASTICSEARCH_FILMS_INDEX')
    elastic_genres_index: str = Field('genres', alias='ELASTICSEARCH_GENRES_INDEX')
    elastic_persons_index: str = Field('persons', alias='ELASTICSEARCH_PERSONS_INDEX')

    # es_id_field: str = ...

    service_url: str = Field('http://localhost:8000', alias='SERVICE_URL')


test_settings = TestSettings()
