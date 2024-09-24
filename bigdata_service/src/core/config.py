# config.py
import os
from logging import config as logging_config

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    bigdata: str = "/bigdata"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class KafkaConfig(BaseModel):
    host: str
    port: int

    topic: str

    @property
    def bootstrap_server(self):
        return f"{self.host}:{self.port}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{os.path.dirname(os.path.abspath(__file__))}/../../.env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="BIGDATA_CONFIG__",
        extra="ignore",
    )
    jwt_secret_key: str = Field(..., alias='JWT_SECRET_KEY')
    jwt_algorithm: str = Field(..., alias='JWT_ALGORITHM')
    api: ApiPrefix = ApiPrefix()
    kafka: KafkaConfig


settings = Settings()
