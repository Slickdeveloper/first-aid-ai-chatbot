"""Application configuration.

This file keeps environment-driven settings in one place so both local development
and future deployment can reuse the same code path.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = BACKEND_ROOT / "first_aid_chatbot.db"


class Settings(BaseSettings):
    # SQLite keeps local development simple; this can be replaced with Postgres later.
    app_name: str = "First Aid AI Chatbot API"
    environment: str = "development"
    database_url: str = Field(
        default=f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
    )
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,"
        "http://localhost:8080,http://127.0.0.1:8080"
    )
    admin_api_key: str = Field(default="")
    auto_ingest_sources: bool = True
    allow_mock_responses: bool = True
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    openai_reasoning_effort: str = "low"

    # Read values from `backend/.env` using an absolute path so scripts work whether
    # they are launched from the backend folder or the project root.
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
    )

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        # The admin key protects write access to the trusted medical knowledge base.
        # Refuse to start with an empty or placeholder key outside of tests.
        if self.environment != "test" and self.admin_api_key.strip() in {"", "change-this-admin-key"}:
            raise ValueError(
                "ADMIN_API_KEY must be set to a non-placeholder value before starting the backend."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    # Cache settings so the app does not re-read environment config on every import.
    # This avoids subtle bugs where different modules might otherwise build different
    # Settings objects during one app run.
    return Settings()
