# AidBot API 合同草案

阶段 0 只固定接口边界，不承诺完整业务逻辑。后续阶段可以替换内部实现，但不应随意破坏这些外部合同。

## 健康检查

`GET /health`

```json
{
  "status": "ok",
  "service": "AidBot",
  "environment": "development"
}
```

## 聊天接口

`POST /api/chat`

请求：

```json
{
  "question": "产品无法联网时如何排查？",
  "conversation_id": null,
  "product_line": null
}
```

响应：

```json
{
  "answer": "...",
  "solution_steps": ["..."],
  "confidence": "low",
  "sources": [],
  "handoff_required": false,
  "handoff_reason": ""
}
```

## 核心类型

`SourceCitation`

```json
{
  "title": "...",
  "source_type": "upload",
  "doc_id": "...",
  "chunk_id": "...",
  "score": 0.82,
  "updated_at": "2026-07-03T00:00:00Z"
}
```

`AnswerResult` 是内部策略输出，统一由 `chat_service` 转成 `ChatResponse`：

```json
{
  "strategy": "template",
  "context": "...",
  "sources": [],
  "confidence": "low",
  "handoff_required": false,
  "handoff_reason": ""
}
```

策略名保留：`template`、`rag`、`local_kb`、`langchain`。后续如果接入 LangGraph，应作为同层策略实现，并继续输出 `AnswerResult`。
