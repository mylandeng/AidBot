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