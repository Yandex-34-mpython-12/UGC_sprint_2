import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore')

    project_name: str = Field('movies', alias='PROJECT_NAME')
    project_version: str = Field('0.0.1', alias='PROJECT_VERSION')
    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: int = Field(6379, alias='REDIS_PORT')
    elastic_host: str = Field('127.0.0.1', alias='ELASTICSEARCH_HOST')
    elastic_port: int = Field(9200, alias='ELASTICSEARCH_PORT')
    elastic_schema: str = Field('http', alias='ELASTICSEARCH_SCHEMA')

    jwt_secret_key: str = Field(..., alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(..., alias='JWT_ALGORITHM')

    jaeger_agent_host_name: str = Field(
        'localhost', alias='JAEGER_AGENT_HOSTNAME')
    jaeger_agent_port: int = Field(6831, alias='JAEGER_AGENT_PORT')

    request_limit_per_minute: int = Field(60, alias='REQUEST_LIMIT_PER_MINUTE')
    enable_tracing: bool = Field(True, alias='ENABLE_TRACING')

    log_level: str = Field('INFO', alias='LOG_LEVEL')

    logger_filename: str = Field(alias='LOGGER_FILENAME')
    logger_maxbytes: int = Field(15000000, alias='LOGGER_MAXBYTES')
    logger_mod: str = Field('a', alias='LOGGER_MOD')
    logger_backup_count: int = Field(5, alias='LOGGER_BACKUP_COUNT')


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
