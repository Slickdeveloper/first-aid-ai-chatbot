"""API-level tests.

These tests check the public contract exposed by FastAPI routes rather than the
internal implementation details of any one service.
"""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.db.models.document_chunk import DocumentChunk
from app.db.models.source_document import SourceDocument
from app.db.session import SessionLocal
from app.main import app


def test_health_check() -> None:
    # The simplest smoke test: if this fails, the backend is not starting correctly.
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_response_contract() -> None:
    # This verifies the response shape for a real grounded question.
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"session_id": "demo-session", "message": "How do I help with a burn?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "citations" in body
    assert body["emergency"] is False
    assert isinstance(body["citations"], list)
    assert body["answer"]


def test_chat_uses_seeded_approved_chunks() -> None:
    # Seed one controlled source/chunk pair so we can prove retrieval is actually
    # using database content instead of hard-coded mock answers.
    db = SessionLocal()
    db.query(DocumentChunk).delete()
    db.query(SourceDocument).delete()
    db.commit()

    source = SourceDocument(
        title="Burns First Aid",
        organization="Test Medical Source",
        source_url="https://example.org/burns",
        content_path="data/sources/burns.txt",
        summary="Approved burns guidance.",
        is_approved=True,
    )
    db.add(source)
    db.flush()
    db.add(
        DocumentChunk(
            source_document_id=source.id,
            chunk_index=0,
            chunk_text="Cool the burn under cool running water for at least 20 minutes.",
            citation_label="Section 1",
            section="Burn care",
        )
    )
    db.commit()
    db.close()

    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"session_id": "retrieval-test", "message": "How do I cool a burn?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["organization"] == "Test Medical Source"
    assert "Burns First Aid" in body["citations"][0]["title"]
    assert "cool running water" in body["answer"].lower()

    db = SessionLocal()
    db.query(DocumentChunk).delete()
    db.query(SourceDocument).delete()
    db.commit()
    db.close()


def test_unknown_topic_refuses_safely() -> None:
    # Unknown topics should refuse safely rather than inventing medical advice.
    client = TestClient(app)
    response = client.post(
        "/chat",
        json={"session_id": "unknown-topic-test", "message": "How do I fix a broken drone propeller?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["citations"] == []
    assert "approved source material" in body["answer"]


def test_admin_sources_include_source_tier() -> None:
    # The admin UI depends on `source_tier` to explain primary vs supporting sources.
    client = TestClient(app)
    response = client.get(
        "/admin/sources",
        headers={"X-Admin-Key": get_settings().admin_api_key},
    )

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert body
    assert "source_tier" in body[0]
