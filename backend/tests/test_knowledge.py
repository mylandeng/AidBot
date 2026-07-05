from fastapi.testclient import TestClient

from app.main import app
from app.services.prompt_service import build_support_prompt
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService, _clean_markdown_for_prompt


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


def test_knowledge_spaces_can_group_sources_and_be_deleted() -> None:
    headers = auth_headers()
    space = client.post(
        "/api/knowledge/spaces",
        json={"name": "产品售后常见问题知识库", "description": "售后 FAQ", "visibility": "internal"},
        headers=headers,
    )
    assert space.status_code == 200
    space_id = space.json()["id"]

    imported = client.post(
        "/api/knowledge/documents",
        json={
            "space_id": space_id,
            "title": "SPACE-9 售后处理",
            "filename": "space-9.html",
            "content_format": "html",
            "content": "<h1>SPACE-9 售后处理</h1><p>SPACE-9 出现 E01 时先重启网关，再检查授权状态。</p>",
            "visibility": "internal",
        },
        headers=headers,
    )
    assert imported.status_code == 200
    assert imported.json()["space_id"] == space_id
    assert imported.json()["content_format"] == "html"

    spaces = client.get("/api/knowledge/spaces", headers=headers)
    assert any(item["id"] == space_id and item["source_count"] >= 1 for item in spaces.json()["items"])

    matched = client.get("/api/knowledge/search", params={"q": "SPACE-9 E01 怎么处理"}, headers=headers)
    assert matched.status_code == 200
    assert matched.json()["items"]

    deleted = client.delete(f"/api/knowledge/spaces/{space_id}", headers=headers)
    assert deleted.status_code == 204

    after_delete = client.get("/api/knowledge/search", params={"q": "SPACE-9 E01 怎么处理"}, headers=headers)
    assert after_delete.status_code == 200
    assert all(item["title"] != "SPACE-9 售后处理" for item in after_delete.json()["items"])


def test_html_document_recall_prioritizes_exact_product_tokens() -> None:
    headers = auth_headers()
    payload = {
        "title": "HTML-7788 芯片低功耗唤醒",
        "filename": "html-7788.html",
        "content_format": "html",
        "content": (
            "<html><body><h1>HTML-7788 芯片手册</h1><h2>低功耗唤醒</h2>"
            "<p>HTML-7788 低功耗唤醒失败时，需要检查 WAKE-PIN-7788 拉高时序，并确认固件版本大于 2.7.1。</p>"
            "</body></html>"
        ),
        "visibility": "internal",
    }

    created = client.post("/api/knowledge/documents", json=payload, headers=headers)
    assert created.status_code == 200
    assert created.json()["content_format"] == "html"

    search = client.get("/api/knowledge/search", params={"q": "WAKE-PIN-7788 低功耗唤醒"}, headers=headers)

    assert search.status_code == 200
    assert search.json()["items"][0]["title"] == payload["title"]


def test_knowledge_source_can_be_deleted() -> None:
    headers = auth_headers()
    created = client.post(
        "/api/knowledge/manual",
        json={
            "title": "DELETE-01 临时知识",
            "content": "DELETE-01 临时知识用于验证删除后不再参与召回。",
            "visibility": "internal",
        },
        headers=headers,
    ).json()

    assert client.delete(f"/api/knowledge/sources/{created['id']}", headers=headers).status_code == 204
    search = client.get("/api/knowledge/search", params={"q": "DELETE-01 临时知识"}, headers=headers)
    assert all(item["title"] != "DELETE-01 临时知识" for item in search.json()["items"])


def test_markdown_splitter_keeps_heading_context_and_merges_short_sections() -> None:
    long_step = "Check power, network, firmware, app status, and collect reproducible evidence. " * 8
    markdown = "\n\n".join(
        [
            "# AX Support Manual",
            "## Offline Issues",
            "### Offline After Pairing",
            long_step,
            "### Offline After Reboot",
            long_step,
            "## Alarm Issues",
            "### Red Light Flashing",
            long_step,
        ]
    )

    chunks = RAGService()._split_text(markdown, chunk_size=700, overlap=80)

    assert 1 < len(chunks) < 6
    assert any("标题路径：AX Support Manual > Offline Issues > Offline After Pairing" in chunk for chunk in chunks)
    assert any("标题路径：AX Support Manual > Alarm Issues > Red Light Flashing" in chunk for chunk in chunks)


def test_html_parser_preserves_heading_context_for_chunking() -> None:
    html = """
    <html>
      <head><style>.hidden { display: none; }</style></head>
      <body>
        <h1>AX-HTML 产品手册</h1>
        <h2>离线问题</h2>
        <p>AX-HTML 配网成功后离线时，先确认指示灯和路由器 2.4G 网络。</p>
        <ul><li>导出设备日志</li><li>检查固件版本</li></ul>
      </body>
    </html>
    """

    parsed = DocumentService().parse_text(html, "html")
    chunks = RAGService()._split_text(parsed, chunk_size=700, overlap=80)

    assert "# AX-HTML 产品手册" in parsed
    assert "## 离线问题" in parsed
    assert "<h1>" not in parsed
    assert any("标题路径：AX-HTML 产品手册 > 离线问题" in chunk for chunk in chunks)
    assert any("导出设备日志" in chunk for chunk in chunks)


def test_prompt_context_strips_markdown_formatting() -> None:
    raw = "\n".join(
        [
            "## 使用方法",
            "**使用方法**：",
            "1. 在项目根目录创建 `.mcp.json` 配置文件",
            "2. 配置 [MCP服务器](https://example.local)",
            "| 工具 | 支持 |",
            "| --- | --- |",
        ]
    )

    cleaned = _clean_markdown_for_prompt(raw)

    assert "**" not in cleaned
    assert "`" not in cleaned
    assert "| ---" not in cleaned
    assert "使用方法：" in cleaned
    assert "在项目根目录创建 .mcp.json 配置文件" in cleaned
    assert "配置 MCP服务器" in cleaned


def test_support_prompt_rewrites_markdown_documents() -> None:
    prompt = build_support_prompt("怎么配置 MCP？", context="**使用方法**：\n1. 创建 `.mcp.json`")

    assert "不得复制标题、加粗、编号清单、表格或原文段落结构" in prompt.system_instruction
    assert "改写成客服可直接发送的自然语言" in prompt.system_instruction
    assert "当前没有命中的知识库片段" not in prompt.knowledge_context


def test_knowledge_source_can_be_reindexed() -> None:
    headers = auth_headers()
    payload = {
        "title": "REINDEX-01 Manual",
        "filename": "reindex-01.md",
        "content": "# REINDEX-01 Manual\n\n## Pairing\n\n" + ("Pairing recovery step. " * 120),
        "visibility": "internal",
    }
    created = client.post("/api/knowledge/markdown", json=payload, headers=headers).json()

    response = client.post(f"/api/knowledge/sources/{created['id']}/reindex", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["chunk_count"] >= 1


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
