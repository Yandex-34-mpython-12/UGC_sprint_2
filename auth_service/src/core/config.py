import logging
import os

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    project_name: str = 'auth'
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: int = logging.DEBUG
    version: str = '0.0.1'


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    oauth: str = "/oauth"
    users: str = "/users"
    roles: str = "/roles"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # v1/auth/login
        parts = (self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")

    @property
    def oauth2_bearer_token_url(self) -> str:
        # v1/oauth/login
        parts = (self.v1.prefix, self.v1.oauth, "/login")
        path = "".join(parts)
        return path.removeprefix("/")


class DatabaseConfig(BaseModel):
    host: str = '127.0.0.1'
    port: int = 5432
    db_name: str
    user: str
    password: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    @property
    def url(self) -> str:
        return f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}'


class CacheConfig(BaseModel):
    host: str
    port: int


class AccessToken(BaseModel):
    jwt_encode_secret: str
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class JaegerConfig(BaseModel):
    enable: bool = True
    agent_host_name: str = 'localhost'
    agent_port: int = 6831


class YandexOauthConfig(BaseModel):
    name: str = 'yandex'
    authorize_url: str = 'https://oauth.yandex.ru/authorize'
    token_url: str = 'https://oauth.yandex.ru/token'
    redirect_uri: str = 'http://localhost/auth/api/v1/oauth/login/yandex'
    user_info_url: str = 'https://login.yandex.ru/info'
    client_id: str
    client_secret: str


class OAuth2Config(BaseModel):
    yandex: YandexOauthConfig
    secret_key: SecretStr


class LoggingConfig(BaseModel):
    log_level: str = 'INFO'

    logger_filename: str = '/app/logs/auth-api-logs.json'  # TODO: rm
    logger_maxbytes: int = 15000000
    logger_mod: str = 'a'
    logger_backup_count: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="AUTH_CONFIG__",
        extra="ignore",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    cache: CacheConfig
    access_token: AccessToken
    jaeger: JaegerConfig = JaegerConfig()
    oauth: OAuth2Config
    logging: LoggingConfig = LoggingConfig()


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
