import json

from app.api import admin, chat
from app.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "admin@aidbot.local", "password": "aidbot123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def sse_payload(body: str, event_name: str) -> dict:
    blocks = body.split("\n\n")
    block = next(item for item in blocks if f"event: {event_name}" in item)
    data_line = next(line for line in block.splitlines() if line.startswith("data: "))
    return json.loads(data_line.removeprefix("data: "))


def test_http_errors_use_structured_contract_and_keep_legacy_detail() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@aidbot.local", "password": "wrong"},
        headers={"X-Request-ID": "req_test_login"},
    )

    assert response.status_code == 401
    assert response.headers["X-Request-ID"] == "req_test_login"
    assert response.json()["detail"] == "Invalid email or password"
    assert response.json()["error"] == {
        "code": "INVALID_CREDENTIALS",
        "message": "邮箱或密码不正确。",
        "retryable": False,
        "request_id": "req_test_login",
        "details": None,
    }


def test_validation_errors_use_structured_contract() -> None:
    response = client.post("/api/chat", json={"question": ""}, headers=auth_headers())

    assert response.status_code == 422
    payload = response.json()["error"]
    assert payload["code"] == "VALIDATION_FAILED"
    assert payload["message"] == "请求参数不正确，请检查后重试。"
    assert payload["retryable"] is False
    assert payload["request_id"].startswith("req_")
    assert payload["details"][0]["field"] == "body.question"


def test_stream_setup_errors_use_same_error_payload() -> None:
    headers = {**auth_headers(), "X-Request-ID": "req_test_retrieval"}
    with client.stream(
        "POST",
        "/api/admin/chat/stream",
        json={"question": "查询外部知识库", "retrieval_provider": "external"},
        headers=headers,
    ) as response:
        body = response.read().decode("utf-8")

    payload = sse_payload(body, "error")
    assert payload["code"] == "RETRIEVAL_UNAVAILABLE"
    assert payload["retryable"] is True
    assert payload["request_id"] == "req_test_retrieval"
    assert "外部知识库尚未配置" in payload["message"]


def test_model_failures_emit_retryable_sse_error(monkeypatch) -> None:
    def fail_stream(*_args, **_kwargs):
        raise RuntimeError("provider secret must not reach the client")
        yield ""

    monkeypatch.setattr(admin.chat_service.llm_service, "stream_answer", fail_stream)
    headers = {**auth_headers(), "X-Request-ID": "req_test_llm"}
    with client.stream("POST", "/api/admin/chat/stream", json={"question": "测试模型异常"}, headers=headers) as response:
        body = response.read().decode("utf-8")

    payload = sse_payload(body, "error")
    assert payload == {
        "code": "LLM_UNAVAILABLE",
        "message": "模型暂时不可用，请稍后重试。",
        "retryable": True,
        "request_id": "req_test_llm",
        "details": None,
    }
    assert "provider secret" not in body


def test_unexpected_http_errors_are_sanitized(monkeypatch) -> None:
    def fail_completion(*_args, **_kwargs):
        raise RuntimeError("database password must not reach the client")

    monkeypatch.setattr(chat.chat_service.llm_service, "complete", fail_completion)
    safe_client = TestClient(app, raise_server_exceptions=False)
    response = safe_client.post(
        "/api/chat",
        json={"question": "测试未知异常"},
        headers={**auth_headers(), "X-Request-ID": "req_test_internal"},
    )

    assert response.status_code == 500
    assert response.json()["error"] == {
        "code": "INTERNAL_ERROR",
        "message": "服务暂时不可用，请稍后重试。",
        "retryable": True,
        "request_id": "req_test_internal",
        "details": None,
    }
    assert response.json()["detail"] == "Internal server error"
    assert "database password" not in response.text
