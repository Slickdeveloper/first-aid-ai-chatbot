"""Shared pytest fixtures for backend tests.

The test suite uses its own SQLite database and seeds approved sources before
each test so results do not depend on whatever happens to be in the developer's
local demo database.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATABASE_PATH = PROJECT_ROOT / "backend" / "test_first_aid_chatbot.db"

# Configure the app before any backend modules are imported by the tests.
os.environ["ENVIRONMENT"] = "test"
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"

import pytest

from app.db.models import AuditLog, ChatLog, DocumentChunk, SourceDocument
from app.db.session import Base, SessionLocal, engine
from app.services.source_ingestion_service import ingest_text_file, list_source_files


@pytest.fixture(autouse=True)
def reset_test_database() -> None:
    # Start each test from a clean schema, then re-seed the approved source corpus.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for source_file in list_source_files():
            ingest_text_file(db, source_file)
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(DocumentChunk).delete()
        db.query(SourceDocument).delete()
        db.query(ChatLog).delete()
        db.query(AuditLog).delete()
        db.commit()
    finally:
        db.close()
