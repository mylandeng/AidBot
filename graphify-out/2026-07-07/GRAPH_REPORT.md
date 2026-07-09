# Graph Report - AidBot  (2026-07-06)

## Corpus Check
- 78 files · ~16,332 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 535 nodes · 976 edges · 41 communities (28 shown, 13 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 106 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `367c00ea`
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
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_create_chat_response|create_chat_response]]
- [[_COMMUNITY_Base|Base]]

## God Nodes (most connected - your core abstractions)
1. `RAGService` - 49 edges
2. `authorized()` - 17 edges
3. `ChatService` - 16 edges
4. `RetrievedChunk` - 16 edges
5. `compilerOptions` - 16 edges
6. `Message` - 13 edges
7. `KnowledgeSourceResponse` - 13 edges
8. `requireSession()` - 13 edges
9. `FeedbackService` - 12 edges
10. `Base` - 11 edges

## Surprising Connections (you probably didn't know these)
- `list_feedback()` --references--> `FeedbackStatus`  [EXTRACTED]
  backend/app/api/feedback.py → frontend/src/lib/types.ts
- `test_long_section_child_chunks_keep_parent_heading_path()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_markdown_splitter_keeps_heading_context_and_merges_short_sections()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `login()` --calls--> `verify_seed_password()`  [INFERRED]
  backend/app/api/auth.py → backend/app/core/security.py
- `get_conversation()` --calls--> `MessageResponse`  [INFERRED]
  backend/app/api/conversations.py → backend/app/schemas/chat.py

## Import Cycles
- None detected.

## Communities (41 total, 13 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.13
Nodes (28): archive_conversation(), delete_conversation(), get_conversation(), _get_owned_conversation(), list_conversations(), CurrentUser, Session, restore_conversation() (+20 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 4 - "CLAUDE.md"
Cohesion: 0.14
Nodes (12): Architecture, Backend (`backend/app`), Commands, Database, Docker (all-in-one), Environment variables, Frontend (`frontend/src`), Graphify knowledge graph (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (14): ensure_runtime_schema(), create_app(), lifespan(), auth_headers(), test_chat_can_continue_existing_conversation(), test_chat_persists_conversation_and_sources_field(), test_conversations_can_be_searched_archived_restored_and_deleted(), test_stream_chat_emits_delta_and_structured_final() (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): AidBot MVP 架构审阅计划, MVP 最短路径, 备注, 推荐开发阶段, 状态, 目标, 证据来源, 遇到的错误 (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (40): create_knowledge_space(), create_manual_knowledge(), delete_knowledge_source(), delete_knowledge_space(), import_knowledge_document(), import_markdown_knowledge(), list_knowledge_sources(), list_knowledge_spaces() (+32 more)

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (52): feedbackOptions, FeedbackWorkbench(), statusFilters, statusLabel(), apiBaseUrl(), archiveConversation(), askQuestion(), askQuestionStream() (+44 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): get_settings(), Settings, BaseSettings

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): AidBot API 合同草案, 健康检查, 核心类型, 聊天接口, 认证接口

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): AidBot, Docker 一键启动, 本地开发, 本机分别启动, 阶段 1 默认登录

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (18): AdminPage(), ChatPage(), ChatWorkbench(), FeedbackPage(), KnowledgePage(), KnowledgeWorkbench(), LoginForm(), LoginPage() (+10 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (18): DocumentService, EmbeddingService, auth_headers(), test_chat_returns_citations_when_knowledge_matches(), test_html_document_recall_prioritizes_exact_product_tokens(), test_html_parser_preserves_heading_context_for_chunking(), test_html_parser_preserves_table_row_relationships(), test_hybrid_search_prioritizes_exact_entity_tokens() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.36
Nodes (7): create_chat_response(), ChatRequest, ChatResponse, CurrentUser, Session, stream_chat_response(), StreamingResponse

### Community 18 - "Community 18"
Cohesion: 0.16
Nodes (14): Any, login(), me(), CurrentUser, _b64decode(), _b64encode(), create_access_token(), decode_access_token() (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (13): create_provider(), LLMCompletion, LLMProvider, LLMService, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., build_support_prompt() (+5 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (23): KnowledgeChunk, KnowledgeDocument, KnowledgeSource, KnowledgeSpace, KnowledgeSourceResponse, KnowledgeSpaceResponse, _clean_markdown_for_prompt(), _heading_path_from_chunk() (+15 more)

### Community 37 - "create_chat_response"
Cohesion: 0.31
Nodes (9): create_feedback(), list_feedback(), CurrentUser, FeedbackCreateRequest, FeedbackItem, FeedbackStatusRequest, Session, update_feedback_status() (+1 more)

### Community 38 - "Base"
Cohesion: 0.33
Nodes (4): Base, Role, User, DeclarativeBase

## Knowledge Gaps
- **97 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `list_feedback()` connect `create_chat_response` to `Community 10`?**
  _High betweenness centrality (0.186) - this node is a cross-community bridge._
- **Why does `FeedbackStatus` connect `Community 10` to `create_chat_response`?**
  _High betweenness centrality (0.181) - this node is a cross-community bridge._
- **Why does `RAGService` connect `Community 22` to `Community 8`, `10. 后续扩展边界`, `Community 20`, `Community 15`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `RAGService` (e.g. with `ChatService` and `KnowledgeChunk`) actually correct?**
  _`RAGService` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `ChatService` (e.g. with `Conversation` and `Message`) actually correct?**
  _`ChatService` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `RetrievedChunk` (e.g. with `KnowledgeChunk` and `KnowledgeDocument`) actually correct?**
  _`RetrievedChunk` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `Service layer boundaries.` to the rest of the system?**
  _102 weakly-connected nodes found - possible documentation gaps or missing edges._