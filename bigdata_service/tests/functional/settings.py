import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    project_name: str
    service_url: str


test_settings = TestSettings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
