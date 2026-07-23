# AidBot 项目开发进度条

本文件是日常推进项目的主看板。每次开始工作前，先对照 `docs/bug-list.md`、`graphify query` 和当前代码；每次完成代码修改后，运行必要测试并执行 `graphify update .`，再更新本文件。

## 当前状态

- 更新日期：2026-07-23
- 当前主线：最近会话 UI 收尾 + 阶段 4 补齐 + 阶段 5/6 建立可审计和发布门槛
- 最近 graph 证据：`graphify query "daily project progress tracker compare task_plan bug-list current graph implemented missing phase status"`
- 当前最大缺口：最近会话折叠展开、反馈按产品线筛选、检索/审计日志、发布 smoke 流程

## 阶段进度

| 阶段 | 状态 | 进度 | 判断 |
|------|------|------|------|
| 阶段 0：项目脚手架与接口合同 | 已完成 | 100% | `backend/`、`frontend/`、`docker-compose.yml`、`.env.example`、API 合同已存在 |
| 阶段 1：认证与最小工作台 | 已完成 | 100% | 登录、token、受保护路由、管理员/访问码路径和认证测试已存在 |
| 阶段 2：问答 MVP 与会话历史 | 已完成 | 100% | 问答、会话持久化、历史查询、单条删除、清空全部聊天记录已完成 |
| 阶段 3：手动知识库与基础 RAG | 基本完成 | 90% | 手动/Markdown/文档导入、切片、embedding、检索、来源引用、重建索引已完成；RAG 质量仍有调优项 |
| 阶段 4：反馈采集与管理员复盘队列 | 进行中 | 75% | 评分、反馈 API/UI、队列和状态流转已完成；缺产品线筛选和自定义处理备注 |
| 阶段 5：知识运维与可审计性 | 未完成 | 30% | 知识列表/状态页已有；缺入库失败可见、持久化 retrieval logs、audit logs、完整追溯链 |
| 阶段 6：MVP 加固与发布门槛 | 未完成 | 45% | 后端核心测试已有；缺统一 smoke 脚本、前端 smoke、日志密钥审查和发布验收清单 |

## 阶段明细

### 阶段 0：项目脚手架与接口合同
- 状态：已完成。
- 已完成：FastAPI 后端、Next.js 前端、Docker Compose、环境变量示例、健康检查、API 合同草案。
- 证据：`backend/app/main.py`、`frontend/src/app`、`docker-compose.yml`、`docs/api-contract.md`。
- 下一步：仅在接口新增时同步 API 合同。

### 阶段 1：认证与最小工作台
- 状态：已完成。
- 已完成：种子管理员登录、访问码登录、当前用户接口、管理员受保护页面、用户聊天入口。
- 证据：`backend/app/api/auth.py`、`backend/app/services/access_key_service.py`、`frontend/src/app/login`、`backend/tests/test_auth.py`。
- 下一步：后续安全审查纳入阶段 6。

### 阶段 2：问答 MVP 与会话历史
- 状态：已完成。
- 已完成：聊天 API、流式回答、会话/消息持久化、历史查询、归档/恢复、单条删除、清空全部聊天记录、用户与管理员调试字段隔离。
- 证据：`backend/app/api/chat.py`、`backend/app/api/conversations.py`、`backend/app/services/chat_service.py`、`backend/tests/test_chat_contract.py`、`frontend/src/lib/api.ts`、`frontend/src/app/chat/workbench.tsx`、`frontend/src/app/admin/chat/workbench.tsx`。
- 验证：`backend/.venv/Scripts/python.exe -m pytest tests/test_chat_contract.py -q` 通过；`npm run build` 通过。
- 下一步：阶段 2 不再阻塞；最近会话默认 5 条和展开交互归入 bug/UI 收尾。

### 阶段 3：手动知识库与基础 RAG
- 状态：基本完成。
- 已完成：知识空间、知识来源、手动知识、Markdown 导入、文档导入、切片、embedding、检索、来源引用、来源删除、空间删除、重建索引。
- 已完成：引用分数裁剪到 0 到 1、相关性门槛、组件冲突过滤、来源多样化。
- 证据：`backend/app/api/knowledge.py`、`backend/app/services/rag_service.py`、`backend/tests/test_knowledge.py`、`frontend/src/app/knowledge/workbench.tsx`。
- 未完成：pgvector/真正全文索引/外部 reranker 仍是后续增强，不阻塞当前 MVP。
- 下一步：优先处理 bug 清单里剩余的最近会话 UI；RAG 质量继续通过 eval fixture 扩展。

### 阶段 4：反馈采集与管理员复盘队列
- 状态：进行中。
- 已完成：用户评分、反馈标签/备注、反馈 API、管理员队列、`pending/processing/resolved/ignored` 状态流转、状态筛选。
- 证据：`backend/app/api/feedback.py`、`backend/app/services/feedback_service.py`、`backend/app/models/feedback.py`、`frontend/src/app/feedback/workbench.tsx`、`backend/tests/test_feedback.py`。
- 未完成：按产品线筛选。
- 未完成：管理员处理反馈时输入自定义备注，而不是只使用固定文案。
- 下一步：给 feedback list 增加 `product_line` 过滤和前端筛选控件；处理状态弹窗支持管理员填写备注。

### 阶段 5：知识运维与可审计性
- 状态：未完成。
- 已完成：管理员可以查看知识项、空间、来源状态和 chunk 数量；可以删除或重建知识来源。
- 证据：`frontend/src/app/knowledge/workbench.tsx`、`backend/app/schemas/knowledge.py`、`backend/app/services/rag_service.py`。
- 未完成：入库任务状态模型还不完整，`IngestionWorker` 仍是占位。
- 未完成：持久化 `retrieval_logs` 表。
- 未完成：关键动作 `audit_logs` 表。
- 未完成：从一次回答追溯到 `message -> retrieval log -> source chunk -> feedback` 的管理员视图。
- 下一步：先建 `retrieval_logs` 和 `audit_logs` 数据模型，再把 `ChatService`/`RAGService`/知识管理动作写入日志。

### 阶段 6：MVP 加固与发布门槛
- 状态：未完成。
- 已完成：后端 auth/chat/knowledge/feedback/health 测试。
- 证据：`backend/tests/test_auth.py`、`backend/tests/test_chat_contract.py`、`backend/tests/test_knowledge.py`、`backend/tests/test_feedback.py`、`backend/tests/test_health.py`。
- 未完成：统一 smoke 流程脚本。
- 未完成：前端 smoke 或端到端浏览器验证。
- 未完成：日志不输出密钥的自动检查。
- 未完成：部署前验收清单。
- 下一步：新增 `docs/release-checklist.md` 或脚本化 smoke 命令，并把必跑命令写入 README。

## Bug 清单对照

| Bug | 当前判断 | 证据 | 下一步 |
|-----|----------|------|--------|
| 聊天输入/输出区域缺少复制能力 | 已完成 | 用户/管理员聊天页均有 `copyText` 和消息复制按钮 | 从 bug 清单标记为已完成 |
| 助手输出未按 Markdown 渲染 | 已完成 | `MessageContent` 支持 heading/list/code/table/quote/inline formatting | 从 bug 清单标记为已完成 |
| 最近会话区域视觉主题不一致 | 待视觉复核 | 聊天页已有统一 sidebar，但未做截图 QA | 用浏览器检查后决定是否关闭 |
| 最近会话展示数量和展开交互需要调整 | 未完成 | 当前 `items.map(...)` 直接渲染全部会话 | 默认 5 条 + 展开 + 悬停滚动条 |
| 引用调试区域用途不清 | 基本完成 | 用户聊天隐藏 debug 字段，管理员聊天保留来源详情 | 复核 UI 文案，必要时从 bug 清单关闭 |
| 引用片段打分和命中可信度偏假 | 基本完成 | RAG 有 relevance gate 和 eval 测试 | 持续增加低相关问题 eval case |
| 引用命中分数超过 1 且跨组件误命中 | 已完成 | `citation()` 裁剪分数，RAG 有组件冲突测试 | 从 bug 清单标记为已完成 |
| 最近会话缺少删除入口和全部清空能力 | 已完成 | 单条删除、`DELETE /api/conversations`、用户/管理员清空入口已完成 | 从 bug 清单标记为已完成 |

## 每日推进流程

1. 运行 `graphify query "<当天要处理的问题>"`，先拿图谱 scoped context。
2. 对照本文件的“阶段进度”和“Bug 清单对照”，只选一个最小闭环任务。
3. 实现代码和测试，避免顺手重构不相关模块。
4. 运行相关测试；涉及前端交互时启动页面做一次浏览器检查。
5. 运行 `graphify update .`。
6. 更新 `docs/task_plan.md` 的进度、证据和下一步；必要时同步 `docs/bug-list.md`、`docs/api-contract.md`、`docs/progress.md`。

## 下一步优先级

1. 最近会话 UI：默认只展示 5 条，支持展开剩余会话，悬停时显示弱化滚动条。
2. 阶段 4 补齐：反馈列表增加产品线筛选，管理员处理反馈时可写自定义备注。
3. 阶段 5 起步：新增 `retrieval_logs` 表，并让聊天回答保存检索证据。
4. 阶段 6 起步：沉淀一条本地 smoke 验收命令或清单。
