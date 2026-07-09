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


def test_admin_can_create_key_and_user_can_login_with_key() -> None:
    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "aidbot123"},
    )
    headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    created = client.post(
        "/api/admin/access-keys",
        json={"name": "客户A", "expires_in": "7d", "max_requests": 10},
        headers=headers,
    )

    assert created.status_code == 200
    access_key = created.json()["access_key"]
    assert access_key.startswith("aidbot_live_")
    assert created.json()["item"]["key_prefix"] in access_key

    login_response = client.post("/api/auth/key-login", json={"access_key": access_key})

    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["user"]["roles"] == ["user"]
    assert payload["user"]["auth_method"] == "access_key"
    assert payload["user"]["key_id"] == created.json()["item"]["id"]


def test_disabled_and_deleted_key_cannot_login() -> None:
    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "aidbot123"},
    )
    headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    created = client.post(
        "/api/admin/access-keys",
        json={"name": "客户B", "expires_in": "7d"},
        headers=headers,
    )
    key_id = created.json()["item"]["id"]
    access_key = created.json()["access_key"]

    disabled = client.post(f"/api/admin/access-keys/{key_id}/disable", headers=headers)
    assert disabled.status_code == 200
    assert client.post("/api/auth/key-login", json={"access_key": access_key}).status_code == 401

    enabled = client.post(f"/api/admin/access-keys/{key_id}/enable", headers=headers)
    assert enabled.status_code == 200
    assert client.post("/api/auth/key-login", json={"access_key": access_key}).status_code == 200

    deleted = client.delete(f"/api/admin/access-keys/{key_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.post("/api/auth/key-login", json={"access_key": access_key}).status_code == 401
