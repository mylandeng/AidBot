# Graph Report - AidBot  (2026-07-24)

## Corpus Check
- 98 files · ~25,105 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 748 nodes · 1455 edges · 57 communities (37 shown, 20 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 189 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `03339eb1`
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
- [[_COMMUNITY_test_chat_contract.py|test_chat_contract.py]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_AidBot MVP 架构审阅进度|AidBot MVP 架构审阅进度]]
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
- [[_COMMUNITY_ChatRequest|ChatRequest]]
- [[_COMMUNITY_CurrentUser|CurrentUser]]
- [[_COMMUNITY_FeedbackCreateRequest|FeedbackCreateRequest]]
- [[_COMMUNITY_FeedbackItem|FeedbackItem]]
- [[_COMMUNITY_FeedbackStatusRequest|FeedbackStatusRequest]]
- [[_COMMUNITY_Session|Session]]
- [[_COMMUNITY_ChatRequest|ChatRequest]]
- [[_COMMUNITY_workbench.tsx|workbench.tsx]]
- [[_COMMUNITY_apiBaseUrl|apiBaseUrl]]

## God Nodes (most connected - your core abstractions)
1. `RAGService` - 57 edges
2. `authorized()` - 23 edges
3. `RetrievedChunk` - 20 edges
4. `AccessKeyService` - 18 edges
5. `ChatService` - 18 edges
6. `utcnow()` - 17 edges
7. `compilerOptions` - 16 edges
8. `Conversation` - 13 edges
9. `Message` - 13 edges
10. `KnowledgeSourceResponse` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_component_conflict_filters_charging_dock_for_controller_query()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_component_conflict_keeps_same_product_strong_match()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_long_section_child_chunks_keep_parent_heading_path()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_markdown_splitter_keeps_heading_context_and_merges_short_sections()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_retrieval_rejects_vector_only_matches_without_text_signal()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py

## Import Cycles
- None detected.

## Communities (57 total, 20 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.43
Nodes (5): Block, isTableStart(), MessageContent(), parseMarkdown(), splitTableRow()

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.17
Nodes (23): ChatService, ChatRequest, ChatResponse, CurrentUser, Session, CurrentUser, Session, end_trace() (+15 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 3 - "AGENTS.md"
Cohesion: 0.22
Nodes (17): archive_conversation(), delete_all_conversations(), delete_conversation(), get_conversation(), _get_owned_conversation(), list_conversations(), CurrentUser, Session (+9 more)

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
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (53): AccessKeyCreateResponse, create_access_key(), delete_access_key(), disable_access_key(), enable_access_key(), list_access_keys(), AccessKeyCreateRequest, ChatRequest (+45 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (29): AdminWorkbench(), durationLabels, archiveConversation(), askQuestion(), authorized(), createAccessKey(), createFeedback(), createKnowledgeSpace() (+21 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (24): AccessKeyCreateRequest, AccessKeyCreateResponse, AccessKeyStatus, ChatRequest, ChatStreamEvent, Confidence, ConversationDetail, ConversationSummary (+16 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (15): AidBot 项目开发进度条, Bug 清单对照, 下一步优先级, 当前状态, 每日推进流程, 阶段 0：项目脚手架与接口合同, 阶段 1：认证与最小工作台, 阶段 2：问答 MVP 与会话历史 (+7 more)

### Community 13 - "Community 13"
Cohesion: 0.27
Nodes (10): create_feedback(), list_feedback(), CurrentUser, FeedbackCreateRequest, FeedbackItem, FeedbackStatusRequest, Session, update_feedback_status() (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (25): AdminChatPage(), AdminPage(), ChatPage(), FeedbackPage(), KnowledgePage(), KnowledgeWorkbench(), LoginForm(), LoginPage() (+17 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (21): auth_headers(), test_chat_returns_citations_when_knowledge_matches(), test_component_conflict_filters_charging_dock_for_controller_query(), test_component_conflict_keeps_same_product_strong_match(), test_html_document_recall_prioritizes_exact_product_tokens(), test_html_parser_preserves_heading_context_for_chunking(), test_html_parser_preserves_table_row_relationships(), test_hybrid_search_prioritizes_exact_entity_tokens() (+13 more)

### Community 16 - "Community 16"
Cohesion: 0.29
Nodes (6): AidBot API 合同草案, 会话接口, 健康检查, 核心类型, 聊天接口, 认证接口

### Community 17 - "admin.py"
Cohesion: 0.08
Nodes (24): create_provider(), LLMCompletion, LLMProvider, LLMService, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., auth_headers() (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (11): AccessKey, AccessKey, AccessKeyService, AccessKeyCreateRequest, CurrentUser, Session, datetime, utcnow() (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (7): AidBot Docker 部署, 使用 GitHub Actions 自动构建, 手动推送到其他镜像仓库, 推送到镜像仓库, 本地开发, 构建生产镜像, 生产注意事项

### Community 21 - "test_chat_contract.py"
Cohesion: 0.33
Nodes (5): AidBot, Docker 一键启动, 本地开发, 本机分别启动, 阶段 1 默认登录

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (27): import_knowledge_document(), _clean_markdown_for_prompt(), _heading_path_from_chunk(), _markdown_sections_for_context(), _merge_entity_metadata(), _parent_section_excerpt(), CurrentUser, Session (+19 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (10): 2026-07-22, AidBot Bug 清单, 助手输出未按 Markdown 渲染, 引用命中分数超过 1 且跨组件误命中, 引用片段打分和命中可信度偏假, 引用调试区域用途不清, 最近会话区域视觉主题不一致, 最近会话展示数量和展开交互需要调整 (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.25
Nodes (6): FeedbackWorkbench(), statusFilters, statusLabel(), listFeedback(), updateFeedbackStatus(), FeedbackItem

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 27 - "AidBot MVP 架构审阅进度"
Cohesion: 0.33
Nodes (5): 2026-07-03, 2026-07-06, 2026-07-07, 2026-07-23, AidBot MVP 架构审阅进度

### Community 37 - "create_chat_response"
Cohesion: 0.13
Nodes (12): create_embedding_provider(), EmbeddingProvider, EmbeddingService, HashEmbeddingProvider, _normalize(), OpenAICompatibleEmbeddingProvider, test_create_embedding_provider_requires_openai_compatible_config(), test_hash_embedding_provider_is_deterministic_and_normalized() (+4 more)

### Community 39 - "阶段.md"
Cohesion: 0.12
Nodes (20): admin_login(), key_login(), login(), me(), CurrentUser, Session, _b64decode(), _b64encode() (+12 more)

### Community 56 - "workbench.tsx"
Cohesion: 0.08
Nodes (23): AdminChatWorkbench(), confidenceLabel(), DeleteDialogState, examples, sourceTypeLabel(), ChatWorkbench(), DeleteDialogState, examples (+15 more)

### Community 57 - "apiBaseUrl"
Cohesion: 0.22
Nodes (9): LoginMode, apiBaseUrl(), askAdminQuestionStream(), askQuestionStream(), askUserQuestionStream(), keyLogin(), login(), parseStreamEvent() (+1 more)

## Knowledge Gaps
- **131 isolated node(s):** `docker-entrypoint.sh script`, `AIDBOT_RUNTIME_API_BASE_URL`, `nextConfig`, `name`, `version` (+126 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RetrievalProvider` connect `Community 10` to `10. 后续扩展边界`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Why does `RAGService` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`, `admin.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `RetrievedChunk` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `RAGService` (e.g. with `ChatService` and `CurrentUser`) actually correct?**
  _`RAGService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `HTTPException` (e.g. with `login()` and `get_conversation()`) actually correct?**
  _`HTTPException` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `RetrievedChunk` (e.g. with `CurrentUser` and `SourceCitation`) actually correct?**
  _`RetrievedChunk` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `Service layer boundaries.` to the rest of the system?**
  _136 weakly-connected nodes found - possible documentation gaps or missing edges._