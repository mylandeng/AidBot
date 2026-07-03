# Graph Report - AidBot  (2026-07-03)

## Corpus Check
- 9 files · ~1,682 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 23 nodes · 20 edges · 5 communities (3 shown, 2 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_AidBot MVP 架构演进图|AidBot MVP 架构演进图]]
- [[_COMMUNITY_10. 后续扩展边界|10. 后续扩展边界]]
- [[_COMMUNITY_7. MVP 模块清单|7. MVP 模块清单]]
- [[_COMMUNITY_AGENTS|AGENTS.md]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]

## God Nodes (most connected - your core abstractions)
1. `AidBot MVP 架构演进图` - 11 edges
2. `10. 后续扩展边界` - 5 edges
3. `7. MVP 模块清单` - 4 edges
4. `graphify` - 1 edges
5. `graphify` - 1 edges
6. `1. 项目定位` - 1 edges
7. `2. MVP 总体架构图` - 1 edges
8. `3. 问答数据流` - 1 edges
9. `4. 知识入库数据流` - 1 edges
10. `5. 管理员反馈闭环` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (5 total, 2 thin omitted)

### Community 0 - "AidBot MVP 架构演进图"
Cohesion: 0.20
Nodes (9): 1. 项目定位, 2. MVP 总体架构图, 3. 问答数据流, 4. 知识入库数据流, 5. 管理员反馈闭环, 6. 阶段演进图, 8. 推荐目录结构, 9. MVP 边界 (+1 more)

### Community 1 - "10. 后续扩展边界"
Cohesion: 0.40
Nodes (5): 10. 后续扩展边界, MCP 接入边界, RAG 服务边界, 权限边界, 质量优化边界

### Community 2 - "7. MVP 模块清单"
Cohesion: 0.50
Nodes (4): 7. MVP 模块清单, 前端, 后端, 数据表 MVP

## Knowledge Gaps
- **17 isolated node(s):** `graphify`, `graphify`, `1. 项目定位`, `2. MVP 总体架构图`, `3. 问答数据流` (+12 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AidBot MVP 架构演进图` connect `AidBot MVP 架构演进图` to `10. 后续扩展边界`, `7. MVP 模块清单`?**
  _High betweenness centrality (0.593) - this node is a cross-community bridge._
- **Why does `10. 后续扩展边界` connect `10. 后续扩展边界` to `AidBot MVP 架构演进图`?**
  _High betweenness centrality (0.268) - this node is a cross-community bridge._
- **Why does `7. MVP 模块清单` connect `7. MVP 模块清单` to `AidBot MVP 架构演进图`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **What connects `graphify`, `graphify`, `1. 项目定位` to the rest of the system?**
  _17 weakly-connected nodes found - possible documentation gaps or missing edges._