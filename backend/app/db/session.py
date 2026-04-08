"""Database session setup.

This file creates the SQLAlchemy engine, the declarative base used by models,
and the per-request session dependency consumed by FastAPI routes.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    # All SQLAlchemy ORM models inherit from this base class.
    pass


settings = get_settings()
engine_kwargs = {"future": True}

if settings.database_url.startswith("sqlite"):
    # SQLite needs this flag when the app and tests share the same connection pool.
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    # FastAPI dependency that provides one database session per request.
    # This keeps DB work scoped to a single request/response cycle and ensures
    # connections are closed even if an error happens.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
