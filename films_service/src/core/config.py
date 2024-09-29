import os

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseModel):
    log_level: str = 'INFO'
    logger_filename: str
    logger_maxbytes: int = 15000000
    logger_mod: str = 'a'
    logger_backup_count: int = 5


class RunConfig(BaseModel):
    project_name: str
    project_version: str = '0.0.1'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
        env_prefix="FILMS_CONFIG__",
    )

    redis_host: str
    redis_port: int
    elastic_host: str
    elastic_port: int
    elastic_schema: str

    jwt_secret_key: str = Field(..., alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(..., alias='JWT_ALGORITHM')

    jaeger_agent_host_name: str = Field(
        'localhost', alias='JAEGER_AGENT_HOSTNAME')
    jaeger_agent_port: int = Field(6831, alias='JAEGER_AGENT_PORT')

    request_limit_per_minute: int
    enable_tracing: bool
    logging: LoggingConfig
    run: RunConfig


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
