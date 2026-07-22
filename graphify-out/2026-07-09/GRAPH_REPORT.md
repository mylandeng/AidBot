# Graph Report - AidBot  (2026-07-09)

## Corpus Check
- 87 files · ~19,132 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 633 nodes · 1207 edges · 46 communities (32 shown, 14 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 134 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93f701fa`
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
- [[_COMMUNITY_阶段|阶段.md]]
- [[_COMMUNITY_feedback.py|feedback.py]]
- [[_COMMUNITY_feedback.py|feedback.py]]
- [[_COMMUNITY_workbench.tsx|workbench.tsx]]
- [[_COMMUNITY_apiBaseUrl|apiBaseUrl]]
- [[_COMMUNITY_workbench.tsx|workbench.tsx]]

## God Nodes (most connected - your core abstractions)
1. `RAGService` - 51 edges
2. `authorized()` - 22 edges
3. `RetrievedChunk` - 19 edges
4. `AccessKeyService` - 18 edges
5. `ChatService` - 18 edges
6. `compilerOptions` - 16 edges
7. `utcnow()` - 15 edges
8. `KnowledgeSourceResponse` - 13 edges
9. `Base` - 11 edges
10. `KnowledgeSource` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_long_section_child_chunks_keep_parent_heading_path()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `test_markdown_splitter_keeps_heading_context_and_merges_short_sections()` --calls--> `RAGService`  [INFERRED]
  backend/tests/test_knowledge.py → backend/app/services/rag_service.py
- `login()` --calls--> `verify_seed_password()`  [INFERRED]
  backend/app/api/auth.py → backend/app/core/security.py
- `get_conversation()` --calls--> `MessageResponse`  [INFERRED]
  backend/app/api/conversations.py → backend/app/schemas/chat.py
- `archive_conversation()` --calls--> `utcnow()`  [INFERRED]
  backend/app/api/conversations.py → backend/app/models/conversation.py

## Import Cycles
- None detected.

## Communities (46 total, 14 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.14
Nodes (24): archive_conversation(), delete_conversation(), get_conversation(), _get_owned_conversation(), list_conversations(), CurrentUser, Session, restore_conversation() (+16 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 4 - "CLAUDE.md"
Cohesion: 0.14
Nodes (12): Architecture, Backend (`backend/app`), Commands, Database, Docker (all-in-one), Environment variables, Frontend (`frontend/src`), Graphify knowledge graph (+4 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (19): create_chat_response(), ChatRequest, ChatResponse, CurrentUser, Session, StreamingResponse, stream_chat_response(), create_user_feedback() (+11 more)

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
Cohesion: 0.13
Nodes (26): AccessKey, AccessKeyCreateRequest, AccessKeyCreateResponse, AccessKeyStatus, ChatRequest, ChatStreamEvent, Confidence, FeedbackCreateRequest (+18 more)

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
Nodes (24): AdminChatPage(), AdminPage(), ChatPage(), FeedbackPage(), KnowledgePage(), LoginForm(), LoginMode, LoginPage() (+16 more)

### Community 15 - "Community 15"
Cohesion: 0.14
Nodes (16): DocumentService, auth_headers(), test_chat_returns_citations_when_knowledge_matches(), test_html_document_recall_prioritizes_exact_product_tokens(), test_html_parser_preserves_heading_context_for_chunking(), test_html_parser_preserves_table_row_relationships(), test_hybrid_search_prioritizes_exact_entity_tokens(), test_knowledge_source_can_be_deleted() (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.40
Nodes (4): 2026-07-03, 2026-07-06, 2026-07-07, AidBot MVP 架构审阅进度

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (17): KnowledgeWorkbench(), archiveConversation(), askQuestion(), authorized(), createFeedback(), createKnowledgeSpace(), createManualKnowledge(), deleteConversation() (+9 more)

### Community 18 - "Community 18"
Cohesion: 0.17
Nodes (12): AccessKey, AccessKey, utcnow(), AccessKeyService, AccessKeyCreateRequest, CurrentUser, Session, CurrentUser (+4 more)

### Community 20 - "Community 20"
Cohesion: 0.09
Nodes (22): create_provider(), LLMCompletion, LLMProvider, LLMService, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., build_support_prompt() (+14 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (25): KnowledgeChunk, KnowledgeDocument, KnowledgeSource, KnowledgeSpace, KnowledgeSourceResponse, KnowledgeSpaceResponse, _clean_markdown_for_prompt(), _heading_path_from_chunk() (+17 more)

### Community 37 - "create_chat_response"
Cohesion: 0.12
Nodes (13): create_embedding_provider(), EmbeddingProvider, EmbeddingService, HashEmbeddingProvider, _normalize(), OpenAICompatibleEmbeddingProvider, test_create_embedding_provider_requires_openai_compatible_config(), test_hash_embedding_provider_is_deterministic_and_normalized() (+5 more)

### Community 39 - "阶段.md"
Cohesion: 0.12
Nodes (20): Any, admin_login(), key_login(), login(), me(), CurrentUser, Session, _b64decode() (+12 more)

### Community 41 - "feedback.py"
Cohesion: 0.20
Nodes (14): AccessKeyCreateResponse, create_access_key(), delete_access_key(), disable_access_key(), enable_access_key(), list_access_keys(), AccessKeyCreateRequest, ChatRequest (+6 more)

### Community 42 - "workbench.tsx"
Cohesion: 0.16
Nodes (12): AdminChatWorkbench(), confidenceLabel(), examples, ChatWorkbench(), examples, createUserFeedback(), getConversation(), listConversations() (+4 more)

### Community 43 - "apiBaseUrl"
Cohesion: 0.20
Nodes (10): HealthBadge(), apiBaseUrl(), askAdminQuestionStream(), askQuestionStream(), askUserQuestionStream(), getHealth(), keyLogin(), login() (+2 more)

### Community 44 - "workbench.tsx"
Cohesion: 0.20
Nodes (8): AdminWorkbench(), durationLabels, createAccessKey(), deleteAccessKey(), disableAccessKey(), enableAccessKey(), listAccessKeys(), AccessKeyDuration

## Knowledge Gaps
- **105 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RetrievalProvider` connect `Community 18` to `Community 10`?**
  _High betweenness centrality (0.149) - this node is a cross-community bridge._
- **Why does `RAGService` connect `Community 22` to `10. 后续扩展边界`, `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `RetrievedChunk` connect `Community 22` to `create_chat_response`, `阶段.md`, `Community 8`, `Community 15`, `Community 18`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `RAGService` (e.g. with `ChatService` and `KnowledgeChunk`) actually correct?**
  _`RAGService` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `HTTPException` (e.g. with `login()` and `get_conversation()`) actually correct?**
  _`HTTPException` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RetrievedChunk` (e.g. with `KnowledgeChunk` and `KnowledgeDocument`) actually correct?**
  _`RetrievedChunk` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `Feedback models are planned for phase 4.` to the rest of the system?**
  _111 weakly-connected nodes found - possible documentation gaps or missing edges._