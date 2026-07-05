# Graph Report - AidBot  (2026-07-05)

## Corpus Check
- 76 files · ~12,745 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 508 nodes · 1244 edges · 38 communities (24 shown, 14 thin omitted)
- Extraction: 61% EXTRACTED · 39% INFERRED · 0% AMBIGUOUS · INFERRED: 489 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `53fbb0c8`
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
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `CurrentUser` - 71 edges
2. `RAGService` - 48 edges
3. `KnowledgeSourceResponse` - 35 edges
4. `KnowledgeSpaceCreate` - 32 edges
5. `KnowledgeSpaceResponse` - 32 edges
6. `ManualKnowledgeCreate` - 32 edges
7. `MarkdownKnowledgeImport` - 32 edges
8. `KnowledgeDocumentImport` - 32 edges
9. `CurrentUser` - 25 edges
10. `ChatRequest` - 24 edges

## Surprising Connections (you probably didn't know these)
- `login()` --calls--> `verify_seed_password()`  [INFERRED]
  backend/app/api/auth.py → backend/app/core/security.py
- `AnswerFeedback` --uses--> `CurrentUser`  [INFERRED]
  backend/app/services/feedback_service.py → backend/app/api/auth.py
- `Any` --uses--> `CurrentUser`  [INFERRED]
  backend/app/core/security.py → backend/app/api/auth.py
- `CurrentUser` --uses--> `CurrentUser`  [INFERRED]
  backend/app/api/feedback.py → backend/app/api/auth.py
- `FeedbackCreate` --uses--> `CurrentUser`  [INFERRED]
  backend/app/api/feedback.py → backend/app/api/auth.py

## Import Cycles
- 1-file cycle: `backend/app/main.py -> backend/app/main.py`
- 1-file cycle: `backend/app/models/conversation.py -> backend/app/models/conversation.py`

## Communities (38 total, 14 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.16
Nodes (32): create_chat_response(), stream_chat_response(), get_conversation(), list_conversations(), CurrentUser, ChatRequest, ChatResponse, CurrentUser (+24 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (20): create_app(), lifespan(), ensure_runtime_schema(), Engine, FastAPI, _clean_markdown_for_prompt(), auth_headers(), test_chat_can_continue_existing_conversation() (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): AidBot MVP 架构审阅计划, MVP 最短路径, 备注, 推荐开发阶段, 状态, 目标, 证据来源, 遇到的错误 (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (42): create_knowledge_space(), create_manual_knowledge(), delete_knowledge_source(), delete_knowledge_space(), import_knowledge_document(), import_markdown_knowledge(), list_knowledge_sources(), list_knowledge_spaces() (+34 more)

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 10 - "Community 10"
Cohesion: 0.12
Nodes (25): BaseModel, CurrentUser, LoginRequest, LoginResponse, AnswerResult, ChatRequest, ChatResponse, ConversationDetail (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): AidBot API 合同草案, 健康检查, 核心类型, 聊天接口, 认证接口

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): AidBot, Docker 一键启动, 本地开发, 本机分别启动, 阶段 1 默认登录

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (18): AdminPage(), conversations, Home(), sources, ChatPage(), ChatWorkbench(), FeedbackPage(), FeedbackWorkbench() (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.22
Nodes (13): Any, login(), me(), CurrentUser, _b64decode(), _b64encode(), create_access_token(), decode_access_token() (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.34
Nodes (18): AnswerFeedback, create_feedback(), list_feedback(), update_feedback_status(), CurrentUser, FeedbackCreate, FeedbackResponse, FeedbackStatusUpdate (+10 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (12): Protocol, create_provider(), LLMCompletion, LLMProvider, LocalSupportProvider, OpenAICompatibleProvider, Deterministic phase-2 provider; replaceable without changing the chat contract., build_support_prompt() (+4 more)

### Community 22 - "Community 22"
Cohesion: 0.17
Nodes (11): Base, datetime, DeclarativeBase, utcnow(), AnswerFeedback, KnowledgeChunk, KnowledgeDocument, KnowledgeSource (+3 more)

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (48): ratingLabels, statusLabels, apiBaseUrl(), askQuestion(), askQuestionStream(), authorized(), createFeedback(), createKnowledgeSpace() (+40 more)

## Knowledge Gaps
- **90 isolated node(s):** `Engine`, `ContentFormat`, `nextConfig`, `name`, `version` (+85 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FastAPI` connect `Community 5` to `10. 后续扩展边界`, `Community 8`, `Community 18`, `Community 19`, `Community 22`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Why does `CurrentUser` connect `10. 后续扩展边界` to `Community 8`, `Community 18`, `Community 19`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `get_conversation()` connect `10. 后续扩展边界` to `Community 8`, `Community 10`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 68 inferred relationships involving `CurrentUser` (e.g. with `AnswerFeedback` and `Any`) actually correct?**
  _`CurrentUser` has 68 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `RAGService` (e.g. with `CurrentUser` and `KnowledgeDocumentImport`) actually correct?**
  _`RAGService` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `KnowledgeSourceResponse` (e.g. with `CurrentUser` and `KnowledgeDocumentImport`) actually correct?**
  _`KnowledgeSourceResponse` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 30 inferred relationships involving `KnowledgeSpaceCreate` (e.g. with `CurrentUser` and `KnowledgeDocumentImport`) actually correct?**
  _`KnowledgeSpaceCreate` has 30 INFERRED edges - model-reasoned connections that need verification._