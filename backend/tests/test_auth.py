from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_auth_status_is_configured() -> None:
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    assert response.json()["status"] == "configured"


def test_login_returns_token_and_user() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "aidbot123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == "admin@aidbot.local"
    assert "admin" in payload["user"]["roles"]


def test_login_rejects_invalid_password() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "wrong"},
    )
    assert response.status_code == 401


def test_me_requires_token() -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_rejects_invalid_token() -> None:
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-token"})
    assert response.status_code == 401


def test_me_returns_current_user_with_token() -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "aidbot123"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["name"] == "售后管理员"
