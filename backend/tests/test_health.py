from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_response_contract() -> None:
    # Verifies the API shape the frontend depends on.
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
