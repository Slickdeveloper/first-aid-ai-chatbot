from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SQLite keeps local development simple; this can be replaced with Postgres later.
    app_name: str = "First Aid AI Chatbot API"
    environment: str = "development"
    database_url: str = Field(
        default="sqlite:///./first_aid_chatbot.db"
    )
    allow_mock_responses: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    # Cache settings so the app does not re-read environment config on every import.
    return Settings()
