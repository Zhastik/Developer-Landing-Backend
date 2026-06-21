from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contact_success():
    response = client.post(
        "/api/contact",
        json={
            "name": "Test User",
            "phone": "+7 999 123-45-67",
            "email": "test@example.com",
            "comment": "Здравствуйте, хочу обсудить backend API для проекта.",
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["ai"]["provider"] in ["fallback", "gemini", "deepseek", "openai", "openrouter", "groq"]


def test_contact_validation_error():
    response = client.post(
        "/api/contact",
        json={
            "name": "A",
            "phone": "1",
            "email": "not-email",
            "comment": "short",
        },
    )
    assert response.status_code == 422
