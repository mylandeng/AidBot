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

## 统一错误合同

所有 HTTP 错误响应都包含统一的 `error` 对象，并通过响应头 `X-Request-ID` 返回同一个请求 ID。为兼容现有客户端，`detail` 字段暂时保留。

```json
{
  "error": {
    "code": "CONVERSATION_ARCHIVED",
    "message": "已归档的会话不能继续提问。",
    "retryable": false,
    "request_id": "req_...",
    "details": null
  },
  "detail": "Archived conversations cannot receive new messages"
}
```

- `code` 是稳定的英文错误码，前端逻辑不得依赖自然语言文案。
- `message` 是可直接展示的中文提示。
- `retryable` 表示用户是否可以在不修改请求的情况下重试。
- `request_id` 用于管理员关联后端日志，不得包含 token、密钥或认证头。
- `details` 只保存安全的校验信息或业务上下文；生产环境的未知异常统一返回 `INTERNAL_ERROR`，不返回堆栈和内部异常文本。

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

聊天和会话接口均要求 `Authorization: Bearer <access_token>`。`GET /api/conversations` 返回当前用户的会话摘要，`GET /api/conversations/{id}` 返回消息历史；`DELETE /api/conversations/{id}` 删除当前用户指定会话，`DELETE /api/conversations` 清空当前用户全部会话；服务端不会返回、删除或影响其他用户的会话。

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
  "space_id": null,
  "product_line": null,
  "retrieval_provider": "local"
}
```

管理员调试入口应传 `space_id`。服务端会校验知识库，从该知识库派生并保存会话 `product_line`，且只检索该知识库；同一会话不能切换到其他产品线。`product_line` 字段暂时保留用于旧客户端兼容，不作为管理员选择知识库的替代。

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

入口差异：

- `POST /api/user/chat/stream`：普通访问码/用户入口，强制 `retrieval_provider="local"`，`final` 事件返回 `UserChatResponse`，不包含 `sources`、`confidence`、`solution_steps`。
- `POST /api/admin/chat/stream`：管理员入口，`final` 事件返回完整 `ChatResponse`，用于引用来源弹窗和调试。
- `POST /api/chat/stream`：内部用户完整入口，保留完整 `ChatResponse`。

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
data: {"code":"LLM_UNAVAILABLE","message":"模型暂时不可用，请稍后重试。","retryable":true,"request_id":"req_...","details":null}
```

SSE `error` 事件与 HTTP 错误使用相同的 `ErrorPayload`。聊天前端必须保留对应的失败回答位置并展示错误；超时标记为失败，用户主动停止标记为“已停止生成”，不能静默删除状态。

## 会话接口

`GET /api/conversations`

返回当前用户的会话摘要列表，服务端默认按最近更新时间倒序返回。

`GET /api/conversations/{conversation_id}`

返回当前用户拥有的一条会话及其消息历史。消息中的 `sources` 使用 `SourceCitation` 结构保存引用来源快照。

`DELETE /api/conversations/{conversation_id}`

删除当前用户的一条会话记录及其消息。若删除的是前端当前打开的会话，前端应回到新会话状态。

响应：`204 No Content`

`DELETE /api/conversations`

清空当前用户的全部会话记录及其消息。该操作只影响当前登录用户，不能删除其他用户的会话。

响应：

```json
{
  "deleted_count": 12
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
  "updated_at": "2026-07-03T00:00:00Z",
  "section_path": "安装 > 联网排查",
  "excerpt": "用于弹窗展示的引用片段摘要。",
  "space_id": "...",
  "space_name": "默认知识空间"
}
```

`score` 的展示语义固定为 0 到 1 的相关性分数；服务端生成引用时必须裁剪异常值，前端不应展示超过 1 的分数。`section_path` 和 `excerpt` 用于引用来源弹窗；`space_id` 和 `space_name` 用于管理员确认命中的知识库。

面向普通用户的聊天流接口不得暴露 `sources`、`confidence`、`solution_steps` 等调试字段；管理员聊天流可以保留完整 `ChatResponse`，并通过回答下方的引用来源弹窗查看来源、片段、分数和知识库归属。

## 知识库接口

`POST /api/knowledge/spaces`

新建知识库时 `product_line` 必填；一个产品线只能对应一个知识库。

```json
{
  "name": "FP10 产品知识库",
  "product_line": "FP10",
  "description": "FP10 全系列手册与售后案例",
  "visibility": "internal"
}
```

`GET /api/knowledge/sources?space_id=<space_id>`

返回指定知识库的源文档。`space_id` 省略时保留旧行为，返回当前用户可见的全部源文档。

`PATCH /api/knowledge/spaces/{space_id}`

修改知识库名称和产品线；旧知识库也可通过该接口补齐产品线。该操作只更新知识库元数据，不需要重新导入文档或重建索引。

```json
{
  "name": "FP10 产品知识库",
  "product_line": "FP10"
}
```

`GET /api/knowledge/search?q=<query>&space_id=<space_id>`

在指定知识库范围内检索；管理员聊天也使用同一 `space_id` 边界，避免跨产品线召回。

## 反馈接口

`GET /api/feedback?status=pending&product_line=FP10`

仅管理员可访问。`status` 和 `product_line` 均为可选筛选参数；产品线取自反馈所属会话，不在反馈表重复存储。

```json
{
  "items": [
    {
      "id": "...",
      "message_id": "...",
      "conversation_id": "...",
      "product_line": "FP10",
      "rating": "needs_review",
      "status": "pending",
      "tags": [],
      "note": "",
      "admin_note": "",
      "question_preview": "...",
      "answer_preview": "...",
      "source_count": 2,
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "product_lines": ["FP10", "FP20"]
}
```

`product_lines` 返回当前管理员反馈队列中可用的非空产品线，用于前端筛选控件；它不受当前 `status` 和 `product_line` 参数影响。

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
