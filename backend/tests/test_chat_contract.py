from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_contract_returns_phase_zero_placeholder() -> None:
    response = client.post("/api/chat", json={"question": "如何处理售后问题？"})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "answer",
        "solution_steps",
        "confidence",
        "sources",
        "handoff_required",
        "handoff_reason",
    }
    assert payload["sources"] == []
