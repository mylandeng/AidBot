from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "admin@aidbot.local", "password": "aidbot123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_answer(headers: dict[str, str]) -> dict:
    response = client.post("/api/chat", json={"question": "如何处理低分回答？"}, headers=headers)
    assert response.status_code == 200
    return response.json()


def test_feedback_requires_authentication() -> None:
    assert client.get("/api/feedback").status_code == 401
    assert client.post("/api/feedback", json={"message_id": "missing", "rating": "not_useful"}).status_code == 401


def test_user_can_create_and_update_answer_feedback() -> None:
    headers = auth_headers()
    answer = create_answer(headers)

    created = client.post(
        "/api/feedback",
        json={"message_id": answer["message_id"], "rating": "not_useful", "tags": ["知识缺失", "知识缺失"], "note": "需要补充排查步骤"},
        headers=headers,
    )
    assert created.status_code == 200
    payload = created.json()
    assert payload["message_id"] == answer["message_id"]
    assert payload["rating"] == "not_useful"
    assert payload["status"] == "pending"
    assert payload["tags"] == ["知识缺失"]
    assert payload["question_preview"]
    assert payload["answer_preview"]

    updated = client.post(
        "/api/feedback",
        json={"message_id": answer["message_id"], "rating": "needs_review", "tags": ["回答组织不好"], "note": "重新看"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["id"] == payload["id"]
    assert updated.json()["rating"] == "needs_review"


def test_admin_can_list_filter_and_process_feedback() -> None:
    headers = auth_headers()
    answer = create_answer(headers)
    created = client.post("/api/feedback", json={"message_id": answer["message_id"], "rating": "needs_review"}, headers=headers).json()

    listing = client.get("/api/feedback", headers=headers)
    assert listing.status_code == 200
    assert any(item["id"] == created["id"] for item in listing.json()["items"])

    processed = client.patch(
        f"/api/feedback/{created['id']}",
        json={"status": "resolved", "admin_note": "已补充到知识库"},
        headers=headers,
    )
    assert processed.status_code == 200
    assert processed.json()["status"] == "resolved"
    assert processed.json()["admin_note"] == "已补充到知识库"

    pending = client.get("/api/feedback", params={"status": "pending"}, headers=headers)
    assert all(item["id"] != created["id"] for item in pending.json()["items"])
