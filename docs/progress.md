# AidBot MVP 架构审阅进度

## 2026-07-03
- 已确认 `docs/mvp-architecture.md` 存在且可读取。
- 已读取项目 `AGENTS.md`；其中要求在可用时，代码库/架构问题应使用 graphify 辅助分析。
- 已运行 graphify query，并读取 `graphify-out/GRAPH_REPORT.md`。
- 已读取完整 MVP 架构文档。
- 已确认当前项目尚无应用脚手架。
- 已创建用于本次架构审阅和开发拆解的规划文件。
- 已完成架构审阅，并将推荐开发阶段写入 `task_plan.md`。
- 已将 `task_plan.md`、`findings.md`、`progress.md` 翻译并整理为中文格式。
- 已完成阶段 0 脚手架：新增 FastAPI 后端、Next.js 前端、Docker Compose、环境变量示例和 API 合同草案。
- 已验证后端测试、前端类型检查和前端生产构建通过；Docker Compose 配置有效。
- 已推进阶段 1 认证基线：新增种子管理员登录、签名 token、当前用户接口、`users/roles` 模型和前端受保护路由。
- 已完成阶段 2 问答 MVP：新增会话/消息持久化、登录用户隔离、可替换 LLM provider、带占位来源的聊天合同、会话历史 API 与交互式聊天 UI。
- 已完成阶段 3 RAG 知识库 MVP 收尾：支持手动知识、Markdown 导入、文档切片、embedding、向量召回、来源引用、重建索引、Markdown prompt 清洗和 provider 无关 prompt builder。
- 已启动阶段 4 质量反馈闭环：回答反馈入口、反馈 API、管理员复盘队列和基础状态流转进入实现。

## 2026-07-06
- 知识库的向量化目前已经做了小切片召回+父级章节回填、hybrid/entity metadata 排序与来源多样化
- chunk数据增加了metadata，并对HTML文件的召回准确率进行了调优
- 还没做的是 pgvector、真正全文索引、外部 reranker、冲突/过期判断。这一版先把结构化数据底座和可评测入口补上了

## 2026-07-07
  用户如何测试

  1. 重建/启动服务：docker compose up --build
  2. 导入几条知识：包含型号、错误码、灯语、中文故障描述。
  3. 在知识库搜索里测：
      - 精确型号/错误码，比如 EVL-920 固件 3.4.1 升级失败
      - 中文关键词，比如 紫灯闪烁三次
      - 模糊组合，比如 升级失败 3.4.1
  4. 在聊天页提问，确认回答引用的 source/chunk 正确。
  5. 跑自动测试：后端 pytest tests/test_knowledge.py。
  6. 可选 DB 验证：确认 vector 扩展、chunk 向量列和 GIN/向量索引已存在。

  注意一点：Postgres 内置全文索引对中文分词不强，售后场景里建议同时做 simple 全文索引 + pg_trgm/精确 token 匹配，保证
  中文、型号、错误码都能稳定召回。

## 2026-07-23
- 已将 `docs/task_plan.md` 从一次性的架构审阅计划改成真实项目开发进度条。
- 已对照 graphify 图谱、当前代码和 `docs/bug-list.md`，标出阶段 0-6 的完成比例、证据文件、未完成项和下一步优先级。
- 已在 `docs/bug-list.md` 为每个问题补充当前状态：复制、Markdown 渲染、引用分数裁剪和组件冲突过滤已完成；最近会话折叠、清空全部聊天记录、反馈产品线筛选、检索/审计日志仍待推进。
- 已完成阶段 2 收尾：新增 `DELETE /api/conversations`，支持当前用户清空全部聊天记录；用户聊天页和管理员聊天页均新增“清空全部”入口。
- 已补充后端合同测试，验证清空全部只删除当前用户会话，不影响其他用户。
- 验证结果：`backend/.venv/Scripts/python.exe -m pytest tests/test_chat_contract.py -q` 通过；`npm run build` 通过。
- 完整后端测试 `backend/.venv/Scripts/python.exe -m pytest tests -q` 当前有 1 个既有 RAG 检索顺序依赖失败，失败用例单独运行通过，需后续单独处理。
- 下一步优先处理最近会话 UI：默认 5 条、展开剩余会话和悬停滚动条。
- 回归修复：删除/清空聊天记录后，再选择历史会话时，管理员“输入要验证的售后问题”区域可能保留旧的阻塞状态。已在用户和管理员聊天页的打开会话、删除当前会话、清空全部和新会话动作中统一复位草稿、弹窗、错误和 `busy` 状态。
- 验证结果：前端 `npm run build` 通过。
