from fastapi.testclient import TestClient
import json

from app.core.database import SessionLocal
from app.main import app
from app.models.conversation import Conversation, Message
from app.services.chat_service import ChatService
from app.services.llm_service import OpenAICompatibleProvider
from app.services.prompt_service import build_support_prompt


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
    assert history.json()["retrieval_provider"] == "local"
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


def test_chat_persists_retrieval_provider_on_new_conversation() -> None:
    headers = auth_headers()
    response = client.post("/api/chat", json={"question": "用本地知识库回答", "retrieval_provider": "local"}, headers=headers)
    assert response.status_code == 200
    detail = client.get(f"/api/conversations/{response.json()['conversation_id']}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["retrieval_provider"] == "local"


def test_external_retrieval_provider_fails_until_configured() -> None:
    headers = auth_headers()
    response = client.post("/api/chat", json={"question": "查外部知识库", "retrieval_provider": "external"}, headers=headers)
    assert response.status_code == 400
    assert "外部知识库尚未配置" in response.json()["detail"]


def test_chat_contextualizes_followup_questions_for_retrieval() -> None:
    db = SessionLocal()
    try:
        conversation = Conversation(user_id="context-user", title="FP10 主控绿灯")
        db.add(conversation)
        db.flush()
        db.add_all(
            [
                Message(conversation_id=conversation.id, role="user", content="FP10 主控绿灯一直闪烁是什么意思？"),
                Message(conversation_id=conversation.id, role="assistant", content="绿灯闪烁表示系统出现故障，需要根据闪烁次数查故障灯语表。"),
            ]
        )
        db.commit()

        contextual = ChatService()._question_with_recent_context(conversation.id, "那闪两下代表啥", db)

        assert "FP10 主控绿灯一直闪烁" in contextual
        assert "绿灯闪烁表示系统出现故障" in contextual
        assert "当前客户问题：那闪两下代表啥" in contextual
    finally:
        db.close()


def test_conversations_can_be_searched_archived_restored_and_deleted() -> None:
    headers = auth_headers()
    first = client.post("/api/chat", json={"question": "AX-900 夜间离线后如何处理？"}, headers=headers).json()
    second = client.post("/api/chat", json={"question": "BX-100 固件升级失败怎么排查？"}, headers=headers).json()

    search = client.get("/api/conversations", params={"q": "BX-100"}, headers=headers)
    assert search.status_code == 200
    assert [item["id"] for item in search.json()] == [second["conversation_id"]]

    archived = client.post(f"/api/conversations/{second['conversation_id']}/archive", headers=headers)
    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"

    default_listing = client.get("/api/conversations", params={"q": "BX-100"}, headers=headers)
    assert all(item["id"] != second["conversation_id"] for item in default_listing.json())

    archived_listing = client.get("/api/conversations", params={"q": "BX-100", "include_archived": "true"}, headers=headers)
    assert any(item["id"] == second["conversation_id"] and item["status"] == "archived" for item in archived_listing.json())

    blocked = client.post("/api/chat", json={"question": "继续这个归档会话", "conversation_id": second["conversation_id"]}, headers=headers)
    assert blocked.status_code == 409

    restored = client.post(f"/api/conversations/{second['conversation_id']}/restore", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["status"] == "active"

    deleted = client.delete(f"/api/conversations/{first['conversation_id']}", headers=headers)
    assert deleted.status_code == 204
    missing = client.get(f"/api/conversations/{first['conversation_id']}", headers=headers)
    assert missing.status_code == 404


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
    assert final_payload["solution_steps"] == []
    assert "型号、固件版本和故障发生时间" not in json.dumps(final_payload, ensure_ascii=False)


def test_openai_provider_adapts_support_prompt_to_chat_messages() -> None:
    provider = OpenAICompatibleProvider("https://llm.example.test", "test-key", "test-model")
    prompt = build_support_prompt("怎么配置 MCP？", product_line="内部工具", context="使用 .mcp.json 配置服务器。")

    messages = provider._messages_for_prompt(prompt)

    assert messages == [
        {"role": "system", "content": prompt.system_instruction},
        {"role": "user", "content": prompt.user_instruction()},
    ]
    assert "产品线：内部工具" in messages[1]["content"]
