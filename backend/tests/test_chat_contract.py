from fastapi.testclient import TestClient
import json

from app.main import app


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "admin@aidbot.local", "password": "aidbot123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_chat_requires_authentication() -> None:
    assert client.post("/api/chat", json={"question": "如何处理售后问题？"}).status_code == 401
    assert client.post("/api/chat/stream", json={"question": "如何处理售后问题？"}).status_code == 401


def test_chat_persists_conversation_and_sources_field() -> None:
    headers = auth_headers()
    response = client.post("/api/chat", json={"question": "如何处理售后问题？"}, headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "conversation_id",
        "message_id",
        "answer",
        "solution_steps",
        "confidence",
        "sources",
        "handoff_required",
        "handoff_reason",
    }
    assert isinstance(payload["sources"], list)
    history = client.get(f"/api/conversations/{payload['conversation_id']}", headers=headers)
    assert history.status_code == 200
    assert [message["role"] for message in history.json()["messages"]] == ["user", "assistant"]


def test_chat_can_continue_existing_conversation() -> None:
    headers = auth_headers()
    first = client.post("/api/chat", json={"question": "第一次提问"}, headers=headers).json()
    second = client.post("/api/chat", json={"question": "继续排查", "conversation_id": first["conversation_id"]}, headers=headers)
    assert second.status_code == 200
    assert second.json()["conversation_id"] == first["conversation_id"]
    listing = client.get("/api/conversations", headers=headers)
    assert listing.status_code == 200
    assert any(item["id"] == first["conversation_id"] and item["message_count"] == 4 for item in listing.json())


def test_stream_chat_emits_delta_and_structured_final() -> None:
    headers = auth_headers()
    with client.stream("POST", "/api/chat/stream", json={"question": "设备离线怎么处理？"}, headers=headers) as response:
        assert response.status_code == 200
        body = response.read().decode("utf-8")

    assert "event: message_start" in body
    assert "event: answer_delta" in body
    assert "event: final" in body
    final_line = next(line for line in body.splitlines() if line.startswith("data: ") and '"message_id"' in line)
    final_payload = json.loads(final_line.removeprefix("data: "))
    assert final_payload["conversation_id"]
    assert final_payload["message_id"]
    assert isinstance(final_payload["sources"], list)
