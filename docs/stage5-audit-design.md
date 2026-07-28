# 阶段 5：知识运维与可审计性设计

## 目标

管理员能够从一条回答追溯到当次检索、命中顺序、知识库、来源片段和后续反馈；知识来源被删除后，历史回答仍保留可读的引用快照。

## 实施顺序

### 1. 建立版本化迁移

- 引入 Alembic，并以当前 SQLAlchemy 模型建立基线。
- 新增结构统一通过迁移脚本发布，不再向 `ensure_runtime_schema()` 追加业务表或字段。
- 保留现有运行时 schema 兼容逻辑一段过渡期，确认已有环境完成迁移后再收缩。

### 2. 保存检索证据

`retrieval_logs` 每次检索一条：

- `id`、`conversation_id`、`user_message_id`、`assistant_message_id`
- `user_id`、`provider`、`product_line`
- `query_text`、`status`、`duration_ms`、`result_count`
- `error_code`、`created_at`

`retrieval_log_items` 每个候选片段一条：

- `retrieval_log_id`、`rank`
- 可空的 `chunk_id`、`source_id`、`space_id`
- `score`
- `citation_snapshot`，保存当时的标题、章节、摘要、知识库名称和来源更新时间

外键删除策略使用 `SET NULL`，同时保留 `citation_snapshot`，避免删除知识来源后历史审计失真。

第一版只覆盖成功回答，并与助手消息在同一事务中提交。第二版再记录检索失败、模型失败和中断请求。

### 3. 保存关键操作

`audit_logs` 记录管理员产生状态变化的动作：

- `actor_user_id`、`action`
- `target_type`、`target_id`
- `metadata`、`created_at`

首批动作包括知识空间/来源创建、导入、重建、删除，以及反馈状态变更。日志不保存访问码、API key、完整 token 或原始认证头。

### 4. 管理员追溯视图

新增只读接口：

- `GET /api/admin/messages/{message_id}/trace`
- `GET /api/admin/retrieval-logs`
- `GET /api/admin/audit-logs`

回答追溯页按“问题与回答 -> 检索概要 -> 命中片段 -> 用户反馈”展示。列表支持时间、用户、产品线、知识库、状态筛选。

## 验收条件

- 一条新回答能够查询到唯一检索记录及有序命中明细。
- 命中明细的分数、知识库和引用摘要与回答保存的 `sources` 一致。
- 删除知识来源后，历史追溯仍能显示引用快照，并明确标记原对象已删除。
- 普通用户不能访问检索日志和审计日志。
- 日志中不出现密钥、token 或认证头。
