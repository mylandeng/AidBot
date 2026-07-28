# AidBot 项目开发进度条

本文件是日常推进项目的主看板。每次开始工作前，先对照 `docs/bug-list.md`、`graphify query` 和当前代码；每次完成代码修改后，运行必要测试并执行 `graphify update .`，再更新本文件。

## 当前状态

- 更新日期：2026-07-28
- 当前主线：聊天/RAG 体验收尾 + 阶段 4 补齐 + 阶段 5/6 建立可审计和发布门槛 + 飞书工作台嵌入路线验证
- 最近 graph 证据：`graphify query "task_plan api-contract SourceCitation 当前进度 长会话回归 文档更新"`
- 当前最大缺口：反馈处理自定义备注、版本化数据库迁移、持久化检索/审计日志、发布 smoke 流程、飞书工作台免登验证

## 阶段进度

| 阶段 | 状态 | 进度 | 判断 |
|------|------|------|------|
| 阶段 0：项目脚手架与接口合同 | 已完成 | 100% | `backend/`、`frontend/`、`docker-compose.yml`、`.env.example`、API 合同已存在 |
| 阶段 1：认证与最小工作台 | 已完成 | 100% | 登录、token、受保护路由、管理员/访问码路径和认证测试已存在 |
| 阶段 2：问答 MVP 与会话历史 | 已完成 | 100% | 问答、会话持久化、历史查询、单条删除、清空全部聊天记录、长会话渲染保护已完成 |
| 阶段 3：手动知识库与基础 RAG | 基本完成 | 96% | 一库一产品线、知识库工作台、手动/文档导入、指定知识库检索、来源引用和重建索引已完成；RAG 质量仍有调优项 |
| 阶段 4：反馈采集与管理员复盘队列 | 进行中 | 90% | 评分、反馈 API/UI、队列、状态流转和产品线筛选已完成；缺自定义处理备注 |
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
- 已完成：聊天页长会话保护，包含请求超时/卸载中止/reader 释放、流式增量批量合并、Markdown memo、默认只渲染最近 80 条消息；用户已完成长会话回归。
- 证据：`backend/app/api/chat.py`、`backend/app/api/conversations.py`、`backend/app/services/chat_service.py`、`backend/tests/test_chat_contract.py`、`frontend/src/lib/api.ts`、`frontend/src/app/chat/workbench.tsx`、`frontend/src/app/admin/chat/workbench.tsx`。
- 验证：`backend/.venv/Scripts/python.exe -m pytest tests/test_chat_contract.py -q` 通过；`npm run build` 通过。
- 下一步：阶段 2 不再阻塞；后续只做小范围交互和视觉验收。

### 阶段 3：手动知识库与基础 RAG
- 状态：基本完成。
- 已完成：知识空间、知识来源、手动知识、Markdown 导入、文档导入、切片、embedding、检索、来源引用、来源删除、空间删除、重建索引。
- 已完成：引用分数裁剪到 0 到 1、相关性门槛、组件冲突过滤、来源多样化、引用来源携带并展示知识库 ID/名称。
- 已完成：一个知识库绑定一条唯一产品线；知识库总览采用卡片布局，详情页展示源文档和片段数，添加知识弹窗支持单条内容与文档导入；旧知识库可原地补充产品线，无需重新索引。
- 已完成：管理员聊天必须选择产品知识库，检索范围固定到该知识库，会话产品线由知识库自动派生；同一会话不能跨产品线切换。
- 已完成：知识库名称/产品线编辑、统一删除确认、无冗余成功提示，以及“正在索引/已建立索引”状态和圆箭头加载交互。
- 证据：`backend/app/api/knowledge.py`、`backend/app/services/rag_service.py`、`backend/tests/test_knowledge.py`、`frontend/src/app/knowledge/workbench.tsx`。
- 未完成：pgvector/真正全文索引/外部 reranker 仍是后续增强，不阻塞当前 MVP。
- 下一步：RAG 质量继续通过低相关问题、组件实体冲突和指定知识库调试场景扩展 eval fixture。

### 阶段 4：反馈采集与管理员复盘队列
- 状态：进行中。
- 已完成：用户评分、反馈标签/备注、反馈 API、管理员队列、`pending/processing/resolved/ignored` 状态流转、状态筛选、按会话产品线筛选。
- 证据：`backend/app/api/feedback.py`、`backend/app/services/feedback_service.py`、`backend/app/models/feedback.py`、`frontend/src/app/feedback/workbench.tsx`、`backend/tests/test_feedback.py`。
- 未完成：管理员处理反馈时输入自定义备注，而不是只使用固定文案。
- 下一步：处理状态弹窗支持管理员填写备注。

### 阶段 5：知识运维与可审计性
- 状态：未完成。
- 已完成：管理员可以查看知识项、空间、来源状态和 chunk 数量；可以删除或重建知识来源。
- 证据：`frontend/src/app/knowledge/workbench.tsx`、`backend/app/schemas/knowledge.py`、`backend/app/services/rag_service.py`。
- 未完成：入库任务状态模型还不完整，`IngestionWorker` 仍是占位。
- 未完成：持久化 `retrieval_logs` 表。
- 未完成：关键动作 `audit_logs` 表。
- 未完成：从一次回答追溯到 `message -> retrieval log -> source chunk -> feedback` 的管理员视图。
- 设计：采用 `retrieval_logs`（一次检索）+ `retrieval_log_items`（排名和引用快照）+ `audit_logs`（管理员动作）三层结构，知识删除后仍保留当时引用快照。
- 实施顺序：先建立 Alembic 迁移基线，再记录成功检索并关联回答消息，然后补失败检索和知识管理审计，最后增加管理员追溯视图。
- 详细方案：`docs/stage5-audit-design.md`。
- 下一步：建立 Alembic 基线迁移和日志模型，不再继续扩展 `ensure_runtime_schema()`。

### 阶段 6：MVP 加固与发布门槛
- 状态：未完成。
- 已完成：后端 auth/chat/knowledge/feedback/health 测试。
- 证据：`backend/tests/test_auth.py`、`backend/tests/test_chat_contract.py`、`backend/tests/test_knowledge.py`、`backend/tests/test_feedback.py`、`backend/tests/test_health.py`。
- 未完成：统一 smoke 流程脚本。
- 未完成：前端 smoke 或端到端浏览器验证。
- 未完成：日志不输出密钥的自动检查。
- 未完成：部署前验收清单。
- 下一步：新增 `docs/release-checklist.md` 或脚本化 smoke 命令，并把必跑命令写入 README。

### 飞书接入专项：工作台 H5 优先，机器人消息增强
- 状态：路线已确认，待实现 POC。
- 官方结论：飞书将机器人和网页应用（H5）定义为不同应用形态；已有 H5 系统可以通过网页应用能力嵌入飞书工作台，并结合 SSO 免登快速迁移。机器人能力可以作为后续增强，与网页应用组合使用。
- 官方参考：`https://open.feishu.cn/document/embed-web-app-into-feishu-workbench/introduction`、`https://open.feishu.cn/document/develop-an-echo-bot/explanation-of-example-code?lang=zh-CN`。
- 推荐主链路：`飞书工作台 -> Next.js H5 -> 飞书身份/免登 -> AidBot API -> ChatService/RAG`。
- 第一阶段：创建网页应用，配置桌面端主页和移动端主页，确认现有 Next.js 页面可在飞书工作台打开。
- 第二阶段：实现飞书用户身份映射和免登校验，把飞书用户映射到现有 `CurrentUser`/权限模型；不改动 `/api/chat` 外部合同。
- 第三阶段：按需补充机器人事件接入，使用飞书官方 SDK 的 `im.message.receive_v1` 和长连接/事件回调，作为群聊问答、通知和快捷入口。
- 消息层设计：参考 OpenClaw 的 Channel Adapter、Gateway、Router、SessionKey、去重和队列，但只实现 AidBot 当前需要的最小子集。
- MCP 边界：工作台嵌入和机器人消息接入均不依赖 MCP；MCP 仅作为未来工具调用或外部知识源协议评估。
- 当前判断：工作台 H5 优先级高于机器人直连，能最快复用现有登录、聊天、知识库和反馈 UI；机器人作为第二入口保留。

## Bug 清单对照

| Bug | 当前判断 | 证据 | 下一步 |
|-----|----------|------|--------|
| 聊天输入/输出区域缺少复制能力 | 已完成 | 用户/管理员聊天页均有 `copyText` 和消息复制按钮 | 从 bug 清单标记为已完成 |
| 助手输出未按 Markdown 渲染 | 已完成 | `MessageContent` 支持 heading/list/code/table/quote/inline formatting | 从 bug 清单标记为已完成 |
| 前端聊天页面 Renderer 内存耗尽 | 已完成 | 流式请求超时/卸载中止/reader 释放，用户已完成长会话回归 | 从 bug 清单标记为已完成 |
| 聊天消息列表无上限，长会话渲染压力过高 | 已完成 | 默认只渲染最近 80 条消息，保留查看完整历史入口 | 从 bug 清单标记为已完成 |
| 流式回答每个增量都会重复解析全部 Markdown | 已完成 | `MessageContent` memo，流式增量按 animation frame 批量合并 | 从 bug 清单标记为已完成 |
| 聊天页面卸载时未自动中止流式请求 | 已完成 | 卸载、切换会话、新请求替换旧请求均会 abort | 从 bug 清单标记为已完成 |
| 最近会话区域视觉主题不一致 | 基本完成 | 聊天页已有统一 sidebar，仍需最终视觉复核 | 用浏览器检查后关闭 |
| 最近会话展示数量和展开交互需要调整 | 已完成 | 折叠按钮和残留状态已移除，全部会话由列表自身滚动；桌面保留 `min(56vh, 560px)`，移动端保留 `180px` 限制 | 从 bug 清单标记为已完成 |
| 引用调试区域用途不清 | 已完成 | 普通用户聊天隐藏 debug 字段，管理员通过回答下方引用来源弹窗查看来源 | 从 bug 清单标记为已完成 |
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

### 业务功能推进
1. 阶段 4 收尾：管理员处理反馈时可写自定义备注。
2. 阶段 5 起步：建立 Alembic 基线，新增 `retrieval_logs`/`retrieval_log_items`，让聊天回答保存检索证据。
3. 阶段 6 起步：沉淀一条本地 smoke 验收命令或清单，覆盖登录、提问、引用来源、会话删除、知识库重建。
4. 飞书工作台 H5 POC：创建网页应用，配置桌面端/移动端主页，验证 Next.js 页面在飞书内打开。
5. RAG eval 扩展：增加低相关问题、组件实体冲突、指定知识库调试的回归样例。

### 技术债务清理（根据 2026-07-28 代码审查）

#### 🔴 高优先级（影响CI和代码质量）
1. **测试隔离问题（已完成）**
   - `test_retrieval_eval_fixture_matches_expected_sources` 改为创建独立评测知识库，并通过 `space_id` 限定导入和搜索范围。
   - 证据：`backend/.venv/Scripts/python.exe -m pytest tests -q` 为 57/57 通过。

2. **添加代码质量门禁**
   - 当前状态：无 linter、无类型检查、无格式化工具
   - 方案：
     * 后端：安装 `ruff`（linter）+ `mypy`（类型检查）
     * 前端：添加 `prettier`（已有 ESLint）
     * 配置 `pre-commit` hooks
   - 配置文件位置：`backend/pyproject.toml`、`frontend/.prettierrc`、`.pre-commit-config.yaml`
   - 优先级：🔴 高（提前发现 80% 类型错误）
   - 预计工作量：1-2 小时
   - 目标：CI 中运行并阻止不合规代码合并

3. **添加前端核心组件测试**
   - 当前状态：21 个 TSX 组件，0 个测试文件（覆盖率 0%）
   - 方案：使用 Jest + React Testing Library
   - 优先测试文件：
     * `frontend/src/components/chat/__tests__/message-content.test.tsx`
     * `frontend/src/app/chat/__tests__/workbench.test.tsx`
     * `frontend/src/lib/__tests__/api.test.ts`
   - 优先级：🟡 中
   - 预计工作量：2-3 小时
   - 目标覆盖率：核心路径 > 60%

#### 🟡 中优先级（提升稳定性）
4. **环境变量验证**
   - 问题：`.env.example` 有 50 行配置，但无验证机制
   - 方案：在 `backend/app/core/config.py` 添加 `validate_config()` 函数
   - 关键检查：生产环境 `AUTH_SECRET_KEY` 不能是默认值、LLM_API_KEY 必填（非 local provider）
   - 优先级：🟡 中
   - 预计工作量：30 分钟

5. **添加 API 性能监控**
   - 当前状态：只有 LangSmith tracing，缺少响应时间指标
   - 方案：
     * 添加 `/health/detail` 端点（数据库连接、provider 状态）
     * 添加 metrics 端点（P50/P95/P99 响应时间）
     * 慢查询日志（>100ms）
   - 优先级：🟡 中
   - 预计工作量：2-3 小时

6. **后端统一错误处理**（重点任务）
   - **现状问题**（2026-07-28 代码审查确认）：
     * `main.py` 没有任何全局异常处理器（无 `@app.exception_handler`），未捕获异常会返回 FastAPI 默认 500，可能泄露堆栈信息
     * 46 处 `HTTPException` 散落在 9 个文件（auth/conversations/chat_service/access_key_service/feedback_service/document_service/rag_service/retrieval_service/security）
     * **错误 detail 格式两套并存且不统一**：
       - 纯字符串：`detail="Knowledge source not found"`（见 `rag_service.py:287,305,414`）
       - 结构化字典：`detail={"code": "KEY_DELETED", "message": "..."}`（见 `access_key_service.py:102-137`）
     * **语言混用**：内部错误用英文（`"Access key not found"`），面向用户的错误用中文，前端需同时兼容两种格式
   - **改造方案**：
     1. 定义统一错误响应模型（如 `{"code": str, "message": str, "detail": dict | None}`），放在 `app/schemas/error.py`
     2. 定义错误码枚举 `app/core/errors.py`（如 `KEY_DELETED`、`SOURCE_NOT_FOUND`、`QUOTA_EXCEEDED` 等），集中管理错误码 → HTTP 状态码 → 默认文案的映射
     3. 自定义业务异常基类 `AppException`，替换散落的 `raise HTTPException`，服务层只抛业务异常、不关心 HTTP 细节
     4. 在 `main.py` 注册全局处理器：
        - `AppException` → 统一结构化响应
        - `RequestValidationError` → 422 统一格式
        - `Exception`（兜底）→ 500，**生产环境隐藏堆栈**、记录日志、返回通用文案
     5. 统一面向用户文案语言（建议中文），内部错误码保持英文常量
   - **注意事项**：
     * 改造需保持 `/api/chat`、`/api/auth` 等**外部合同不破坏**，前端错误处理逻辑（`frontend/src/lib/api.ts` 的 SSE `error` 事件解析）要同步核对
     * 流式接口（`chat.py:/stream`）的错误走 SSE `error` 事件，不是 HTTP 状态码，需单独确认统一格式如何落到流式协议
     * 补充测试：每类异常至少一个用例，验证响应结构、状态码、生产环境不泄露堆栈
   - **相关文件**：`backend/app/main.py`、`backend/app/core/errors.py`（新建）、`backend/app/schemas/error.py`（新建）、上述 9 个抛异常文件、`frontend/src/lib/api.ts`、`frontend/src/lib/types.ts`
   - 优先级：🟡 中（用户重点关注项）
   - 预计工作量：4-6 小时（含测试和前端联调）

7. **Docker 镜像优化**
   - 当前状态：单阶段构建
   - 方案：使用多阶段构建减少镜像体积 40-60%
   - 文件：`backend/Dockerfile`、`frontend/Dockerfile`
   - 优先级：🟡 中
   - 预计工作量：1 小时

#### 🟢 低优先级（长期演进）
8. **数据库迁移工具**
   - 当前方案：`Base.metadata.create_all()` + `ensure_runtime_schema()`
   - 建议：引入 Alembic 做版本化迁移
   - 优先级：🟢 低
   - 阻塞因素：当前方案足够，暂无痛点

9. **前端状态管理重构**
   - 问题：`workbench.tsx` 本地状态过多（messages、conversations、isStreaming 等）
   - 建议：引入 Zustand 或提取自定义 hooks
   - 优先级：🟢 低
   - 触发条件：状态逻辑复杂度进一步增加时考虑

10. **安全加固**
   - 建议项：
     * API rate limiting（FastAPI-Limiter）
     * 安全 headers（CSP、X-Frame-Options）
     * 输入验证加强
     * 敏感字段脱敏日志
   - 优先级：🟢 低（纳入阶段 6 安全审查）

#### 📊 当前技术指标
- **测试覆盖**: 后端 ~40%（估算），前端 0%
- **测试通过率**: 100%（57/57）
- **代码质量工具**: 无 linter、无类型检查
- **文档覆盖**: README + CLAUDE.md + api-contract.md + task_plan.md
- **类型安全**: Python 类型忽略仅 1 处，前端 0 个 `any` 类型 ✅

#### 参考文档
详细优化计划和技术债务分析见 `docs/optimization-plan.md`
