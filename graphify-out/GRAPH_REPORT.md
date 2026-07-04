# Graph Report - AidBot  (2026-07-05)

## Corpus Check
- 72 files · ~8,749 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 404 nodes · 763 edges · 41 communities (23 shown, 18 thin omitted)
- Extraction: 69% EXTRACTED · 31% INFERRED · 0% AMBIGUOUS · INFERRED: 237 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b14390ed`
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
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `CurrentUser` - 46 edges
2. `RAGService` - 30 edges
3. `ChatRequest` - 24 edges
4. `KnowledgeSourceResponse` - 23 edges
5. `ManualKnowledgeCreate` - 22 edges
6. `MarkdownKnowledgeImport` - 22 edges
7. `ChatService` - 19 edges
8. `ChatResponse` - 17 edges
9. `Conversation` - 16 edges
10. `Message` - 16 edges

## Surprising Connections (you probably didn't know these)
- `login()` --calls--> `verify_seed_password()`  [INFERRED]
  backend/app/api/auth.py → backend/app/core/security.py
- `Any` --uses--> `CurrentUser`  [INFERRED]
  backend/app/core/security.py → backend/app/api/auth.py
- `ChatRequest` --uses--> `CurrentUser`  [INFERRED]
  backend/app/api/chat.py → backend/app/api/auth.py
- `ChatResponse` --uses--> `CurrentUser`  [INFERRED]
  backend/app/api/chat.py → backend/app/api/auth.py
- `CurrentUser` --uses--> `CurrentUser`  [INFERRED]
  backend/app/api/chat.py → backend/app/api/auth.py

## Import Cycles
- 1-file cycle: `backend/app/main.py -> backend/app/main.py`
- 1-file cycle: `backend/app/models/conversation.py -> backend/app/models/conversation.py`

## Communities (41 total, 18 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.13
Nodes (33): create_chat_response(), stream_chat_response(), get_conversation(), list_conversations(), ChatRequest, ChatResponse, CurrentUser, Session (+25 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (11): create_app(), lifespan(), FastAPI, auth_headers(), test_chat_can_continue_existing_conversation(), test_chat_persists_conversation_and_sources_field(), test_stream_chat_emits_delta_and_structured_final(), auth_headers() (+3 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): AidBot MVP 架构审阅计划, MVP 最短路径, 备注, 推荐开发阶段, 状态, 目标, 证据来源, 遇到的错误 (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.19
Nodes (25): create_manual_knowledge(), import_markdown_knowledge(), list_knowledge_sources(), search_knowledge(), CurrentUser, CurrentUser, KnowledgeSourceResponse, ManualKnowledgeCreate (+17 more)

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 10 - "Community 10"
Cohesion: 0.17
Nodes (17): BaseModel, CurrentUser, LoginRequest, LoginResponse, AnswerResult, ChatRequest, ChatResponse, ConversationDetail (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): AidBot API 合同草案, 健康检查, 核心类型, 聊天接口, 认证接口

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): AidBot, Docker 一键启动, 本地开发, 本机分别启动, 阶段 1 默认登录

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (15): AdminPage(), conversations, Home(), sources, ChatPage(), ChatWorkbench(), FeedbackPage(), KnowledgePage() (+7 more)

### Community 18 - "Community 18"
Cohesion: 0.22
Nodes (13): Any, login(), me(), CurrentUser, _b64decode(), _b64encode(), create_access_token(), decode_access_token() (+5 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (8): Protocol, create_provider(), LLMCompletion, LLMProvider, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., _support_prompt()

### Community 22 - "Community 22"
Cohesion: 0.24
Nodes (7): Base, DeclarativeBase, KnowledgeChunk, KnowledgeDocument, KnowledgeSource, Role, User

### Community 27 - "Community 27"
Cohesion: 0.12
Nodes (29): HealthBadge(), apiBaseUrl(), askQuestion(), askQuestionStream(), authorized(), createManualKnowledge(), getConversation(), getHealth() (+21 more)

## Knowledge Gaps
- **86 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+81 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FastAPI` connect `Community 5` to `Community 8`, `10. 后续扩展边界`, `Community 18`, `Community 22`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `CurrentUser` connect `Community 8` to `10. 后续扩展边界`, `Community 18`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `LLMService` connect `10. 后续扩展边界` to `Community 20`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `CurrentUser` (e.g. with `Any` and `CurrentUser`) actually correct?**
  _`CurrentUser` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `RAGService` (e.g. with `CurrentUser` and `KnowledgeSourceResponse`) actually correct?**
  _`RAGService` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `ChatRequest` (e.g. with `CurrentUser` and `ChatRequest`) actually correct?**
  _`ChatRequest` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `KnowledgeSourceResponse` (e.g. with `CurrentUser` and `CurrentUser`) actually correct?**
  _`KnowledgeSourceResponse` has 20 INFERRED edges - model-reasoned connections that need verification._