# Graph Report - AidBot  (2026-07-28)

## Corpus Check
- 101 files · ~28,602 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 832 nodes · 1594 edges · 56 communities (41 shown, 15 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `318055f0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_AidBot MVP 架构演进图|AidBot MVP 架构演进图]]
- [[_COMMUNITY_10. 后续扩展边界|10. 后续扩展边界]]
- [[_COMMUNITY_7. MVP 模块清单|7. MVP 模块清单]]
- [[_COMMUNITY_AGENTS|AGENTS.md]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_admin.py|admin.py]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_compilerOptions|compilerOptions]]
- [[_COMMUNITY_test_chat_contract.py|test_chat_contract.py]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_AidBot MVP 架构审阅进度|AidBot MVP 架构审阅进度]]
- [[_COMMUNITY_workbench.tsx|workbench.tsx]]
- [[_COMMUNITY_create_chat_response|create_chat_response]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY_conftest.py|conftest.py]]
- [[_COMMUNITY_create_chat_response|create_chat_response]]
- [[_COMMUNITY_Base|Base]]
- [[_COMMUNITY_阶段|阶段.md]]
- [[_COMMUNITY_feedback.py|feedback.py]]
- [[_COMMUNITY_feedback.py|feedback.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY___init__.py|__init__.py]]
- [[_COMMUNITY_FeedbackCreateRequest|FeedbackCreateRequest]]
- [[_COMMUNITY_FeedbackItem|FeedbackItem]]
- [[_COMMUNITY_workbench.tsx|workbench.tsx]]
- [[_COMMUNITY_apiBaseUrl|apiBaseUrl]]

## God Nodes (most connected - your core abstractions)
1. `RAGService` - 60 edges
2. `authorized()` - 25 edges
3. `RetrievedChunk` - 20 edges
4. `ChatService` - 19 edges
5. `AccessKeyService` - 18 edges
6. `utcnow()` - 17 edges
7. `compilerOptions` - 16 edges
8. `Conversation` - 14 edges
9. `Message` - 13 edges
10. `KnowledgeSourceResponse` - 13 edges

## Surprising Connections (you probably didn't know these)
- `list_feedback()` --references--> `FeedbackStatus`  [EXTRACTED]
  backend/app/api/feedback.py → frontend/src/lib/types.ts
- `test_component_conflict_filters_charging_dock_for_controller_query()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_component_conflict_keeps_same_product_strong_match()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_long_section_child_chunks_keep_parent_heading_path()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_markdown_splitter_keeps_heading_context_and_merges_short_sections()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py

## Import Cycles
- None detected.

## Communities (56 total, 15 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.38
Nodes (5): Block, isTableStart(), MessageContent, parseMarkdown(), splitTableRow()

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.16
Nodes (25): UserChatResponse, ChatService, ChatRequest, ChatResponse, CurrentUser, Session, CurrentUser, Session (+17 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.07
Nodes (28): 1. 修复测试隔离问题 ✅, 1. 环境变量验证 (30分钟), 2. 添加 Docker 多阶段构建 (1小时), 2. 添加代码质量门禁, 3. 添加 API 健康检查详情 (30分钟), 3. 添加前端核心组件测试, AidBot 优化计划, 🔧 Quick Wins (快速见效) (+20 more)

### Community 3 - "AGENTS.md"
Cohesion: 0.42
Nodes (13): archive_conversation(), delete_all_conversations(), delete_conversation(), get_conversation(), _get_owned_conversation(), list_conversations(), CurrentUser, Session (+5 more)

### Community 4 - "CLAUDE.md"
Cohesion: 0.14
Nodes (12): Architecture, Backend (`backend/app`), Commands, Database, Docker (all-in-one), Environment variables, Frontend (`frontend/src`), Graphify knowledge graph (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (24): create_chat_response(), ChatRequest, ChatResponse, CurrentUser, Session, StreamingResponse, stream_chat_response(), create_user_feedback() (+16 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.34
Nodes (7): FeedbackService, CurrentUser, FeedbackCreateRequest, FeedbackItem, FeedbackStatusRequest, Session, AnswerFeedback

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (56): AccessKeyCreateResponse, create_access_key(), delete_access_key(), disable_access_key(), enable_access_key(), list_access_keys(), AccessKeyCreateRequest, ChatRequest (+48 more)

### Community 9 - "Community 9"
Cohesion: 0.10
Nodes (20): AddMode, Dialog, KnowledgeWorkbench(), archiveConversation(), askQuestion(), authorized(), createFeedback(), createKnowledgeSpace() (+12 more)

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (29): Window, AccessKey, AccessKeyCreateRequest, AccessKeyCreateResponse, AccessKeyStatus, ChatRequest, ChatResponse, ChatStreamEvent (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.09
Nodes (22): AidBot 项目开发进度条, Bug 清单对照, 下一步优先级, 业务功能推进, 🟡 中优先级（提升稳定性）, 🟢 低优先级（长期演进）, 参考文档, 📊 当前技术指标 (+14 more)

### Community 13 - "Community 13"
Cohesion: 0.31
Nodes (9): create_feedback(), list_feedback(), CurrentUser, FeedbackCreateRequest, FeedbackItem, FeedbackStatusRequest, Session, update_feedback_status() (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (26): AdminChatPage(), AdminPage(), ChatPage(), FeedbackPage(), KnowledgePage(), LoginForm(), LoginMode, LoginPage() (+18 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (22): auth_headers(), test_chat_returns_citations_when_knowledge_matches(), test_component_conflict_filters_charging_dock_for_controller_query(), test_component_conflict_keeps_same_product_strong_match(), test_html_document_recall_prioritizes_exact_product_tokens(), test_html_parser_preserves_heading_context_for_chunking(), test_html_parser_preserves_table_row_relationships(), test_hybrid_search_prioritizes_exact_entity_tokens() (+14 more)

### Community 16 - "Community 16"
Cohesion: 0.22
Nodes (8): AidBot API 合同草案, 会话接口, 健康检查, 反馈接口, 核心类型, 知识库接口, 聊天接口, 认证接口

### Community 17 - "admin.py"
Cohesion: 0.09
Nodes (24): create_provider(), LLMCompletion, LLMProvider, LLMService, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., auth_headers() (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.20
Nodes (9): AccessKey, AccessKey, AccessKeyService, AccessKeyCreateRequest, CurrentUser, Session, datetime, utcnow() (+1 more)

### Community 19 - "Community 19"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 20 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 21 - "test_chat_contract.py"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (29): KnowledgeChunk, KnowledgeDocument, KnowledgeSource, KnowledgeSpace, KnowledgeSourceResponse, KnowledgeSpaceResponse, _clean_markdown_for_prompt(), _heading_path_from_chunk() (+21 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (19): 2026-07-22, 2026-07-27, 2026-07-28, AI 引用来源缺少知识库归属, AidBot Bug 清单, 全局成功提示冗余且删除确认不统一, 前端聊天页面 Renderer 内存耗尽, 助手输出未按 Markdown 渲染 (+11 more)

### Community 24 - "Community 24"
Cohesion: 0.29
Nodes (5): FeedbackWorkbench(), statusFilters, statusLabel(), listFeedback(), updateFeedbackStatus()

### Community 27 - "AidBot MVP 架构审阅进度"
Cohesion: 0.29
Nodes (6): 2026-07-03, 2026-07-06, 2026-07-07, 2026-07-23, 2026-07-28, AidBot MVP 架构审阅进度

### Community 28 - "workbench.tsx"
Cohesion: 0.17
Nodes (10): AdminWorkbench(), durationLabels, DeleteConfirmDialog(), DeleteConfirmDialogProps, createAccessKey(), deleteAccessKey(), disableAccessKey(), enableAccessKey() (+2 more)

### Community 31 - "__init__.py"
Cohesion: 0.22
Nodes (8): 交互约束, 产品约束, 参考结论, 添加知识弹窗, 知识库工作台设计, 知识库总览, 知识库详情, 页面结构

### Community 34 - "__init__.py"
Cohesion: 0.22
Nodes (8): 1. 建立版本化迁移, 2. 保存检索证据, 3. 保存关键操作, 4. 管理员追溯视图, 实施顺序, 目标, 阶段 5：知识运维与可审计性设计, 验收条件

### Community 37 - "create_chat_response"
Cohesion: 0.12
Nodes (13): create_embedding_provider(), EmbeddingProvider, EmbeddingService, HashEmbeddingProvider, _normalize(), OpenAICompatibleEmbeddingProvider, test_create_embedding_provider_requires_openai_compatible_config(), test_hash_embedding_provider_is_deterministic_and_normalized() (+5 more)

### Community 39 - "阶段.md"
Cohesion: 0.12
Nodes (20): admin_login(), key_login(), login(), me(), CurrentUser, Session, _b64decode(), _b64encode() (+12 more)

### Community 40 - "feedback.py"
Cohesion: 0.12
Nodes (14): AidBot 部署指南, 使用 GitHub Actions 自动构建, 手动推送到其他镜像仓库, 推送到镜像仓库, 本地开发, 构建生产镜像, 生产注意事项, AidBot (+6 more)

### Community 56 - "workbench.tsx"
Cohesion: 0.08
Nodes (22): AdminChatWorkbench(), confidenceLabel(), DeleteDialogState, examples, sourceTypeLabel(), ChatWorkbench(), DeleteDialogState, examples (+14 more)

### Community 57 - "apiBaseUrl"
Cohesion: 0.25
Nodes (8): apiBaseUrl(), askAdminQuestionStream(), askQuestionStream(), askUserQuestionStream(), keyLogin(), login(), parseStreamEvent(), streamChat()

## Knowledge Gaps
- **182 isolated node(s):** `docker-entrypoint.sh script`, `AIDBOT_RUNTIME_API_BASE_URL`, `nextConfig`, `name`, `version` (+177 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RetrievalProvider` connect `10. 后续扩展边界` to `Community 10`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `RAGService` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `RetrievedChunk` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `RAGService` (e.g. with `ChatService` and `KnowledgeChunk`) actually correct?**
  _`RAGService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `HTTPException` (e.g. with `login()` and `get_conversation()`) actually correct?**
  _`HTTPException` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `RetrievedChunk` (e.g. with `KnowledgeChunk` and `KnowledgeDocument`) actually correct?**
  _`RetrievedChunk` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `Service layer boundaries.` to the rest of the system?**
  _187 weakly-connected nodes found - possible documentation gaps or missing edges._