import os

from pydantic import BaseModel, Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class LoggingConfig(BaseModel):
    log_level: str = 'INFO'

    logger_filename: str
    logger_maxbytes: int = 15000000
    logger_mod: str = 'a'
    logger_backup_count: int = 5


class MongoConfig(BaseModel):
    mongodb_uri: MongoDsn
    mongodb_db_name: str


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
    logging: LoggingConfig
    mongo: MongoConfig


settings = Settings()
