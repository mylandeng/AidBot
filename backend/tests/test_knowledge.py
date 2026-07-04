from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "admin@aidbot.local", "password": "aidbot123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_knowledge_requires_authentication() -> None:
    assert client.get("/api/knowledge/sources").status_code == 401
    assert client.post("/api/knowledge/manual", json={"title": "离线处理", "content": "确认网络和设备状态。"}).status_code == 401


def test_manual_knowledge_can_be_indexed_and_retrieved() -> None:
    headers = auth_headers()
    payload = {
        "title": "AX-42 配网后 App 显示离线",
        "content": "AX-42 配网成功但 App 显示离线时，先确认设备指示灯常亮，再检查路由器 2.4G 网络和 DNS。若三分钟后仍离线，重新上电并导出设备日志转人工。",
        "visibility": "internal",
    }

    created = client.post("/api/knowledge/manual", json=payload, headers=headers)
    assert created.status_code == 200
    assert created.json()["chunk_count"] >= 1

    search = client.get("/api/knowledge/search", params={"q": "AX-42 App 离线 怎么排查"}, headers=headers)
    assert search.status_code == 200
    assert search.json()["items"]
    assert search.json()["items"][0]["title"] == payload["title"]


def test_markdown_import_is_indexed_as_upload_source() -> None:
    headers = auth_headers()
    payload = {
        "title": "MD-77 重启循环处理",
        "filename": "md-77-reboot.md",
        "content": "# MD-77 重启循环处理\n\nMD-77 设备每五分钟重启一次时，先检查电源适配器输出，再清理最近一次异常配置。若仍循环重启，导出启动日志并转人工。",
        "visibility": "internal",
    }

    created = client.post("/api/knowledge/markdown", json=payload, headers=headers)
    assert created.status_code == 200
    assert created.json()["source_type"] == "upload"
    assert created.json()["chunk_count"] >= 1

    search = client.get("/api/knowledge/search", params={"q": "MD-77 每五分钟重启"}, headers=headers)
    assert search.status_code == 200
    assert search.json()["items"][0]["source_type"] == "upload"
    assert search.json()["items"][0]["title"] == payload["title"]


def test_chat_returns_citations_when_knowledge_matches() -> None:
    headers = auth_headers()
    client.post(
        "/api/knowledge/manual",
        json={
            "title": "ZX-9 指示灯红色闪烁",
            "content": "ZX-9 指示灯红色闪烁代表传感器自检失败。请先断电十秒，再检查传感器排线；仍失败时需要转人工维修。",
            "visibility": "internal",
        },
        headers=headers,
    )

    response = client.post("/api/chat", json={"question": "ZX-9 红灯闪烁怎么处理？"}, headers=headers)
    assert response.status_code == 200
    sources = response.json()["sources"]
    assert sources
    assert sources[0]["source_type"] == "manual"
    assert sources[0]["title"] == "ZX-9 指示灯红色闪烁"
