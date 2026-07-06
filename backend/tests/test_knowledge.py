import json
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.core.database import SessionLocal
from app.services.prompt_service import build_support_prompt
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService, RetrievedChunk, _clean_markdown_for_prompt
from app.models.knowledge import KnowledgeChunk, KnowledgeDocument, KnowledgeSource


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


def test_long_section_child_chunks_keep_parent_heading_path() -> None:
    markdown = "\n\n".join(
        [
            "# FP10 Service Manual",
            "## Battery Faults",
            "### LED5 Purple Blink",
            "LED5 purple blink 4 times means charge over-current. " * 24,
        ]
    )

    chunks = RAGService()._split_text(markdown, chunk_size=260, overlap=40)

    assert len(chunks) > 1
    assert all(chunk.startswith("标题路径：FP10 Service Manual > Battery Faults > LED5 Purple Blink") for chunk in chunks)


def test_context_block_backfills_parent_section_for_small_chunk() -> None:
    document = KnowledgeDocument(
        id="doc-parent",
        title="FP10 Manual",
        source_id="source-parent",
        content=(
            "# FP10 Manual\n\n"
            "## Battery Faults\n\n"
            "### LED5 Purple Blink\n\n"
            "确认电池温度、充电器规格和日志时间戳。\n"
            "LED5 紫灯闪烁 4 次代表充电过流，需要停止充电并检查线束。"
        ),
    )
    source = KnowledgeSource(id="source-parent", title="FP10 电池手册", owner_user_id="user")
    chunk = KnowledgeChunk(
        id="chunk-parent",
        document_id=document.id,
        source_id=source.id,
        title="FP10 Manual",
        content="标题路径：FP10 Manual > Battery Faults > LED5 Purple Blink\nLED5 紫灯闪烁 4 次代表充电过流。",
        embedding=[],
    )

    block = RetrievedChunk(chunk, source, document, 1.0).context_block()

    assert "父级章节：FP10 Manual > Battery Faults > LED5 Purple Blink" in block
    assert "章节回填：" in block
    assert "确认电池温度、充电器规格和日志时间戳" in block
    assert "命中片段：" in block


def test_imported_chunks_store_section_and_entity_metadata() -> None:
    headers = auth_headers()
    payload = {
        "title": "META-710 电池灯语说明",
        "filename": "meta-710.md",
        "content": "# META-710 Service\n\n## 电池灯语\n\nMETA-710 出现 LED6 紫灯闪烁 2 次时，检查电池线束和固件 2.8.3。",
        "visibility": "internal",
    }

    created = client.post("/api/knowledge/markdown", json=payload, headers=headers)
    assert created.status_code == 200

    db = SessionLocal()
    try:
        source = db.scalar(select(KnowledgeSource).where(KnowledgeSource.title == payload["title"]))
        assert source is not None
        assert source.search_metadata["products"] == ["META-710"]
        assert "LED6" in source.search_metadata["fault_codes"]

        document = db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.source_id == source.id))
        assert document is not None
        assert document.sections
        assert document.sections[0]["path"] == "META-710 Service > 电池灯语"

        chunk = db.scalar(select(KnowledgeChunk).where(KnowledgeChunk.source_id == source.id))
        assert chunk is not None
        assert chunk.section_path == "META-710 Service > 电池灯语"
        assert "META-710" in chunk.entities["products"]
        assert "LED6" in chunk.entities["fault_codes"]
        assert "2.8.3" in chunk.entities["versions"]
        assert "电池" in chunk.entities["components"]
    finally:
        db.close()


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


def test_html_parser_preserves_table_row_relationships() -> None:
    html = """
    <html>
      <body>
        <h1>FP10 电池状态指示灯说明</h1>
        <table>
          <tr><th>故障类型</th><th>指示灯状态</th><th>闪烁规律</th></tr>
          <tr><td>充电过流</td><td><img alt="LED5 紫色" /></td><td>持续闪烁 4 次</td></tr>
        </table>
      </body>
    </html>
    """

    parsed = DocumentService().parse_text(html, "html")

    assert "# FP10 电池状态指示灯说明" in parsed
    assert "充电过流 | LED5 紫色 | 持续闪烁 4 次" in parsed
    assert "故障类型：充电过流；指示灯状态：LED5 紫色；闪烁规律：持续闪烁 4 次" in parsed


def test_retrieval_diversifies_top_sources() -> None:
    service = RAGService()
    document = KnowledgeDocument(id="doc", title="doc", source_id="source-a", content="content")
    source_a = KnowledgeSource(id="source-a", title="主控说明书", owner_user_id="user")
    source_b = KnowledgeSource(id="source-b", title="电池灯语说明", owner_user_id="user")
    ranked = [
        RetrievedChunk(KnowledgeChunk(id="a1", document_id="doc", source_id="source-a", title="A1", content="A1", embedding=[]), source_a, document, 0.9),
        RetrievedChunk(KnowledgeChunk(id="a2", document_id="doc", source_id="source-a", title="A2", content="A2", embedding=[]), source_a, document, 0.8),
        RetrievedChunk(KnowledgeChunk(id="b1", document_id="doc", source_id="source-b", title="B1", content="B1", embedding=[]), source_b, document, 0.7),
    ]

    selected = service._diversify_sources(ranked, limit=2)

    assert [item.source.id for item in selected] == ["source-a", "source-b"]


def test_hybrid_search_prioritizes_exact_entity_tokens() -> None:
    headers = auth_headers()
    client.post(
        "/api/knowledge/manual",
        json={
            "title": "HYB-901 电池灯语精确说明",
            "content": "HYB-901 出现 LED5 紫灯闪烁 4 次时，代表充电过流。处理方式是停止充电，检查充电器和电池线束。",
            "visibility": "internal",
        },
        headers=headers,
    )
    client.post(
        "/api/knowledge/manual",
        json={
            "title": "通用灯语排查说明",
            "content": "红灯闪烁、紫灯闪烁和离线告警都需要检查网络、电源、固件和日志。灯语排查时先收集用户描述。",
            "visibility": "internal",
        },
        headers=headers,
    )

    search = client.get("/api/knowledge/search", params={"q": "HYB-901 LED5 紫灯闪烁 4 次"}, headers=headers)

    assert search.status_code == 200
    assert search.json()["items"][0]["title"] == "HYB-901 电池灯语精确说明"


def test_retrieval_eval_fixture_matches_expected_sources() -> None:
    headers = auth_headers()
    cases = json.loads((Path(__file__).parent / "fixtures" / "rag_retrieval_eval.json").read_text(encoding="utf-8"))
    documents = [
        {
            "title": "EVL-910 电池灯语处理",
            "content": "# EVL-910 维修手册\n\n## 电池灯语\n\nEVL-910 出现 LED7 紫灯闪烁 3 次代表电池温度传感异常，应停止使用并检查电池线束。",
        },
        {
            "title": "EVL-920 固件升级失败",
            "content": "# EVL-920 固件手册\n\n## 版本 3.4.1 升级失败\n\nEVL-920 固件 3.4.1 升级失败时，先校验升级包，再重启网关。",
        },
        {
            "title": "通用灯语排查",
            "content": "紫灯闪烁、红灯闪烁和升级失败都需要收集日志，但没有具体型号时不能判断具体故障。",
        },
    ]

    for document in documents:
        response = client.post(
            "/api/knowledge/markdown",
            json={**document, "filename": f"{document['title']}.md", "visibility": "internal"},
            headers=headers,
        )
        assert response.status_code == 200

    for case in cases:
        expected = case["expected_entities"]
        extracted = RAGService()._extract_entities(case["query"])
        for key, values in expected.items():
            for value in values:
                assert value in extracted[key]

        search = client.get("/api/knowledge/search", params={"q": case["query"]}, headers=headers)
        assert search.status_code == 200
        assert search.json()["items"][0]["title"] == case["expected_title"]


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


def test_support_prompt_forbids_inferred_fault_light_mappings() -> None:
    prompt = build_support_prompt("主控绿灯闪两次是什么故障？", context="故障灯语对照表存在于图片中。")

    assert "必须逐字命中知识库中的具体条目才能回答" in prompt.system_instruction
    assert "不得根据优先级、相邻条目、常识或图片标题推断未列出的映射" in prompt.system_instruction
    assert "当前知识库未解析该图片表格" in prompt.system_instruction


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
