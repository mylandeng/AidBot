# Graph Report - AidBot  (2026-07-03)

## Corpus Check
- 65 files · ~3,389 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 247 nodes · 228 edges · 51 communities (22 shown, 29 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2312eebb`
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
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 16 edges
2. `ChatRequest` - 14 edges
3. `AidBot MVP 架构演进图` - 11 edges
4. `FastAPI` - 9 edges
5. `AnswerRouter` - 9 edges
6. `ChatResponse` - 8 edges
7. `AidBot MVP 架构审阅计划` - 8 edges
8. `推荐开发阶段` - 8 edges
9. `TemplateStrategy` - 7 edges
10. `ChatService` - 6 edges

## Surprising Connections (you probably didn't know these)
- `AnswerResult` --uses--> `ChatRequest`  [INFERRED]
  backend/app/services/strategies/template_strategy.py → backend/app/api/chat.py
- `ChatRequest` --uses--> `ChatRequest`  [INFERRED]
  backend/app/services/strategies/template_strategy.py → backend/app/api/chat.py
- `AnswerRouter` --uses--> `ChatRequest`  [INFERRED]
  backend/app/services/chat_service.py → backend/app/api/chat.py
- `ChatRequest` --uses--> `ChatService`  [INFERRED]
  backend/app/api/chat.py → backend/app/services/chat_service.py
- `AnswerResult` --uses--> `ChatRequest`  [INFERRED]
  backend/app/services/answer_router.py → backend/app/api/chat.py

## Import Cycles
- 1-file cycle: `backend/app/main.py -> backend/app/main.py`

## Communities (51 total, 29 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.10
Nodes (19): 10. 后续扩展边界, 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 7. MVP 模块清单 (+11 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.20
Nodes (13): AnswerRouter, create_chat_response(), ChatRequest, ChatResponse, AnswerResult, ChatRequest, ChatRequest, ChatResponse (+5 more)

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.10
Nodes (20): dependencies, next, react, react-dom, devDependencies, eslint, eslint-config-next, @types/node (+12 more)

### Community 6 - "Community 6"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (15): AidBot MVP 架构审阅计划, MVP 最短路径, 备注, 推荐开发阶段, 状态, 目标, 证据来源, 遇到的错误 (+7 more)

### Community 8 - "Community 8"
Cohesion: 0.21
Nodes (8): HealthBadge(), getHealth(), ChatRequest, ChatResponse, Confidence, HealthResponse, SourceCitation, SourceType

### Community 9 - "Community 9"
Cohesion: 0.29
Nodes (6): AidBot MVP 架构审阅发现, 初步审阅发现, 当前项目状态, 推荐决策, 架构审阅, 架构文档摘要

### Community 10 - "Community 10"
Cohesion: 0.53
Nodes (5): BaseModel, AnswerResult, ChatRequest, ChatResponse, SourceCitation

### Community 11 - "Community 11"
Cohesion: 0.50
Nodes (3): BaseSettings, get_settings(), Settings

### Community 12 - "Community 12"
Cohesion: 0.40
Nodes (4): AidBot API 合同草案, 健康检查, 核心类型, 聊天接口

### Community 13 - "Community 13"
Cohesion: 0.40
Nodes (4): AidBot, Docker 一键启动, 本地开发, 本机分别启动

## Knowledge Gaps
- **83 isolated node(s):** `nextConfig`, `name`, `version`, `private`, `dev` (+78 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_chat_response()` connect `10. 后续扩展边界` to `Community 5`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `ChatRequest` (e.g. with `AnswerRouter` and `ChatRequest`) actually correct?**
  _`ChatRequest` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `AnswerRouter` (e.g. with `AnswerRouter` and `ChatRequest`) actually correct?**
  _`AnswerRouter` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AidBot backend package.`, `Core configuration and infrastructure.`, `SQLAlchemy models will be added in later phases.` to the rest of the system?**
  _95 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `AidBot MVP 架构演进图` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Should `7. MVP 模块清单` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `Community 5` be split into smaller, more focused modules?**
  _Cohesion score 0.10526315789473684 - nodes in this community are weakly interconnected._