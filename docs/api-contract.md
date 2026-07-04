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

## 认证接口

阶段 1 使用内置种子管理员账号验证登录链路：

- 邮箱：`admin@aidbot.local`
- 密码：`aidbot123`

生产环境必须通过环境变量覆盖默认密码和 `AUTH_SECRET_KEY`。

`GET /api/auth/status`

```json
{
  "status": "configured",
  "provider": "seed_admin"
}
```

`POST /api/auth/login`

请求：

```json
{
  "email": "admin@aidbot.local",
  "password": "aidbot123"
}
```

响应：

```json
{
  "conversation_id": "...",
  "message_id": "...",
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "id": "seed-admin",
    "email": "admin@aidbot.local",
    "name": "售后管理员",
    "roles": ["admin", "support"]
  }
}
```

聊天和会话接口均要求 `Authorization: Bearer <access_token>`。`GET /api/conversations` 返回当前用户的会话摘要，`GET /api/conversations/{id}` 返回消息历史；服务端不会返回其他用户的会话。

`GET /api/auth/me`

请求头：

```text
Authorization: Bearer <access_token>
```

响应：

```json
{
  "id": "seed-admin",
  "email": "admin@aidbot.local",
  "name": "售后管理员",
  "roles": ["admin", "support"]
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
  "conversation_id": "...",
  "message_id": "...",
  "answer": "...",
  "solution_steps": ["..."],
  "confidence": "low",
  "sources": [],
  "handoff_required": false,
  "handoff_reason": ""
}
```

`POST /api/chat/stream`

返回 `text/event-stream`。流式事件只用于前端展示中的打字机效果；结构化结果以后端 `final` 事件为准，前端不得从模型自然语言中反推结构化字段。

事件：

```text
event: message_start
data: {"conversation_id":"..."}

event: answer_delta
data: {"delta":"..."}

event: final
data: {"conversation_id":"...","message_id":"...","answer":"...","solution_steps":["..."],"confidence":"low","sources":[],"handoff_required":false,"handoff_reason":""}
```

错误：

```text
event: error
data: {"message":"模型暂时不可用，请稍后重试。"}
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
