import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class ClickhouseConfig(BaseModel):
    host: str
    port: int
    scheme: str

    @property
    def url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"


class KafkaConfig(BaseModel):
    host: str
    port: int

    topic: str

    @property
    def bootstrap_server(self):
        return f"{self.host}:{self.port}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="ignore",
    )
    ch: ClickhouseConfig
    kafka: KafkaConfig


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
