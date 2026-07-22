# Graph Report - AidBot  (2026-07-22)

## Corpus Check
- 92 files · ~22,983 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 717 nodes · 1409 edges · 57 communities (38 shown, 19 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 187 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3e238715`
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
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
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

## God Nodes (most connected - your core abstractions)
1. `RAGService` - 57 edges
2. `authorized()` - 22 edges
3. `RetrievedChunk` - 20 edges
4. `AccessKeyService` - 18 edges
5. `ChatService` - 18 edges
6. `utcnow()` - 17 edges
7. `compilerOptions` - 16 edges
8. `Message` - 13 edges
9. `KnowledgeSourceResponse` - 13 edges
10. `Base` - 12 edges

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

## Communities (57 total, 19 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.43
Nodes (5): Block, isTableStart(), MessageContent(), parseMarkdown(), splitTableRow()

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.16
Nodes (25): UserChatResponse, ChatService, ChatRequest, ChatResponse, CurrentUser, Session, CurrentUser, Session (+17 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 3 - "AGENTS.md"
Cohesion: 0.44
Nodes (12): archive_conversation(), delete_conversation(), get_conversation(), _get_owned_conversation(), list_conversations(), CurrentUser, Session, restore_conversation() (+4 more)

### Community 4 - "CLAUDE.md"
Cohesion: 0.14
Nodes (12): Architecture, Backend (`backend/app`), Commands, Database, Docker (all-in-one), Environment variables, Frontend (`frontend/src`), Graphify knowledge graph (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (25): create_chat_response(), ChatRequest, ChatResponse, CurrentUser, Session, StreamingResponse, stream_chat_response(), create_feedback() (+17 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (36): create_knowledge_space(), create_manual_knowledge(), delete_knowledge_source(), delete_knowledge_space(), import_knowledge_document(), import_markdown_knowledge(), list_knowledge_sources(), list_knowledge_spaces() (+28 more)

### Community 9 - "Community 9"
Cohesion: 0.15
Nodes (15): KnowledgeWorkbench(), archiveConversation(), askQuestion(), authorized(), createFeedback(), createKnowledgeSpace(), createManualKnowledge(), deleteKnowledgeSource() (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (27): AccessKey, AccessKeyCreateRequest, AccessKeyCreateResponse, AccessKeyStatus, ChatRequest, ChatResponse, ChatStreamEvent, Confidence (+19 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.15
Nodes (18): AccessKeyCreateResponse, create_access_key(), delete_access_key(), disable_access_key(), enable_access_key(), list_access_keys(), AccessKeyCreateRequest, ChatRequest (+10 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (15): AidBot MVP 架构审阅计划, MVP 最短路径, 备注, 推荐开发阶段, 状态, 目标, 证据来源, 遇到的错误 (+7 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (26): AdminChatPage(), AdminPage(), ChatPage(), FeedbackPage(), KnowledgePage(), LoginForm(), LoginMode, LoginPage() (+18 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (20): auth_headers(), test_chat_returns_citations_when_knowledge_matches(), test_component_conflict_filters_charging_dock_for_controller_query(), test_component_conflict_keeps_same_product_strong_match(), test_html_document_recall_prioritizes_exact_product_tokens(), test_html_parser_preserves_heading_context_for_chunking(), test_html_parser_preserves_table_row_relationships(), test_hybrid_search_prioritizes_exact_entity_tokens() (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.30
Nodes (10): auth_headers(), test_admin_chat_stream_route_keeps_debug_fields(), test_chat_can_continue_existing_conversation(), test_chat_persists_conversation_and_sources_field(), test_chat_persists_retrieval_provider_on_new_conversation(), test_conversations_can_be_searched_archived_restored_and_deleted(), test_external_retrieval_provider_fails_until_configured(), test_key_user_cannot_call_legacy_debug_chat_endpoint() (+2 more)

### Community 17 - "Community 17"
Cohesion: 0.28
Nodes (8): create_user_feedback(), ChatRequest, CurrentUser, FeedbackCreateRequest, FeedbackItem, Session, StreamingResponse, stream_user_chat()

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (11): AccessKey, AccessKey, AccessKeyService, AccessKeyCreateRequest, CurrentUser, Session, datetime, utcnow() (+3 more)

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (8): apiBaseUrl(), askAdminQuestionStream(), askQuestionStream(), askUserQuestionStream(), keyLogin(), login(), parseStreamEvent(), streamChat()

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (12): create_provider(), LLMCompletion, LLMProvider, LLMService, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., test_openai_provider_adapts_support_prompt_to_chat_messages() (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.20
Nodes (8): AdminWorkbench(), durationLabels, createAccessKey(), deleteAccessKey(), disableAccessKey(), enableAccessKey(), listAccessKeys(), AccessKeyDuration

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (30): _clean_markdown_for_prompt(), _heading_path_from_chunk(), _markdown_sections_for_context(), _merge_entity_metadata(), _parent_section_excerpt(), CurrentUser, Session, RAGService (+22 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (10): 2026-07-22, AidBot Bug 清单, 助手输出未按 Markdown 渲染, 引用命中分数超过 1 且跨组件误命中, 引用片段打分和命中可信度偏假, 引用调试区域用途不清, 最近会话区域视觉主题不一致, 最近会话展示数量和展开交互需要调整 (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.29
Nodes (5): FeedbackWorkbench(), statusFilters, statusLabel(), listFeedback(), updateFeedbackStatus()

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 27 - "Community 27"
Cohesion: 0.33
Nodes (5): AidBot API 合同草案, 健康检查, 核心类型, 聊天接口, 认证接口

### Community 28 - "Community 28"
Cohesion: 0.33
Nodes (5): AidBot, Docker 一键启动, 本地开发, 本机分别启动, 阶段 1 默认登录

### Community 29 - "Community 29"
Cohesion: 0.40
Nodes (4): 2026-07-03, 2026-07-06, 2026-07-07, AidBot MVP 架构审阅进度

### Community 37 - "create_chat_response"
Cohesion: 0.12
Nodes (13): create_embedding_provider(), EmbeddingProvider, EmbeddingService, HashEmbeddingProvider, _normalize(), OpenAICompatibleEmbeddingProvider, test_create_embedding_provider_requires_openai_compatible_config(), test_hash_embedding_provider_is_deterministic_and_normalized() (+5 more)

### Community 39 - "阶段.md"
Cohesion: 0.12
Nodes (20): admin_login(), key_login(), login(), me(), CurrentUser, Session, _b64decode(), _b64encode() (+12 more)

### Community 56 - "workbench.tsx"
Cohesion: 0.10
Nodes (17): AdminChatWorkbench(), confidenceLabel(), examples, sourceTypeLabel(), ChatWorkbench(), examples, feedbackReasons, PendingFeedback (+9 more)

## Knowledge Gaps
- **117 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RAGService` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Why does `RetrievalProvider` connect `10. 后续扩展边界` to `Community 10`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `RetrievedChunk` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `RAGService` (e.g. with `ChatService` and `CurrentUser`) actually correct?**
  _`RAGService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `HTTPException` (e.g. with `login()` and `get_conversation()`) actually correct?**
  _`HTTPException` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `RetrievedChunk` (e.g. with `CurrentUser` and `SourceCitation`) actually correct?**
  _`RetrievedChunk` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `Service layer boundaries.` to the rest of the system?**
  _122 weakly-connected nodes found - possible documentation gaps or missing edges._