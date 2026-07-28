# AidBot 优化计划

**更新时间**: 2026-07-28
**当前状态**: 后端 62/62 测试通过；前端类型检查与生产构建通过，基础功能完备，进入优化阶段

---

## 🎯 立即行动项 (本周完成)

### 1. 修复测试隔离问题 ✅
**原问题**: `test_retrieval_eval_fixture_matches_expected_sources` 在完整测试套件中失败，单独运行通过
**原因**: 评估测试未限定知识库，前序测试数据会进入检索候选集
**已完成**: 为评估夹具创建独立知识库，并通过 `space_id` 限定检索范围；完整测试套件现为 57/57 通过

### 2. 添加代码质量门禁
**当前状态**: 前端已有 TypeScript 类型检查；后端尚无统一的 linter 与静态类型门禁
**方案**:
```bash
# 1. 安装工具
pip install ruff mypy
npm install -D prettier

# 2. 配置文件
# backend/pyproject.toml
[tool.ruff]
line-length = 140
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true

# 3. 添加到 pre-commit
pip install pre-commit
```
**预期收益**: 提前发现80%的类型错误和代码风格问题
**优先级**: 🔴 高

### 3. 添加前端核心组件测试
**当前状态**: 0个测试文件
**方案**: 优先覆盖3个核心组件
```bash
npm install -D @testing-library/react @testing-library/jest-dom jest-environment-jsdom

# 目标测试文件:
# frontend/src/components/chat/__tests__/message-content.test.tsx
# frontend/src/app/chat/__tests__/workbench.test.tsx
# frontend/src/lib/__tests__/api.test.ts
```
**目标覆盖率**: 核心路径 > 60%
**优先级**: 🟡 中

---

## 📊 技术债务清单

### 测试覆盖缺口
| 模块 | 当前状态 | 目标 | 缺失场景 |
|------|---------|------|---------|
| `rag_service.py` | 部分覆盖 | 80% | 混合检索边界情况、多样性算法 |
| `chat_service.py` | 基础覆盖 | 70% | 流式错误处理、超时重试 |
| `retrieval_service.py` | 良好 | 85% | 外部provider失败降级 |
| 前端组件 | 0% | 60% | 用户交互、SSE流处理 |

### 性能监控缺失
- [ ] API响应时间 P50/P95/P99
- [ ] RAG检索延迟分布
- [ ] 数据库慢查询日志 (>100ms)
- [ ] 前端首屏渲染时间

### 安全加固
- [ ] 添加 rate limiting (FastAPI-Limiter)
- [ ] CSP headers (Content-Security-Policy)
- [ ] 输入验证加强 (pydantic validator)
- [ ] 敏感字段脱敏日志

---

## 🚀 架构演进建议

### 阶段1: 稳定性 (1-2周)
1. ✅ 修复测试隔离
2. [ ] 添加 ruff + mypy
3. [ ] 前端核心测试
4. [ ] 添加 API metrics 端点

### 阶段2: 可观测性 (2-3周)
1. 结构化日志 (loguru)
2. Grafana + Prometheus 监控
3. 错误追踪 (Sentry 或 LangSmith)
4. 性能基线测试

### 阶段3: 高级特性 (1个月+)
1. 数据库迁移工具 (Alembic)
2. 前端状态管理重构 (Zustand)
3. 知识库版本管理
4. A/B测试框架

---

## 🔧 Quick Wins (快速见效)

### 1. 环境变量验证 (30分钟)
```python
# backend/app/core/config.py
def validate_config(settings: Settings) -> None:
    if settings.app_env == "production":
        assert settings.auth_secret_key != "change-this-dev-secret", "生产环境必须设置 AUTH_SECRET_KEY"
        assert settings.llm_api_key or settings.llm_provider == "local", "生产环境必须配置 LLM_API_KEY"
```

### 2. 添加 Docker 多阶段构建 (1小时)
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
WORKDIR /app
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
```
**收益**: 镜像体积减少 40-60%

### 3. 添加 API 健康检查详情 (30分钟)
```python
@router.get("/health/detail")
def health_detail(db: Session = Depends(get_db)):
    return {
        "status": "healthy",
        "database": "connected" if db.execute("SELECT 1").scalar() == 1 else "disconnected",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "version": "0.1.0",
    }
```

---

## 📝 文档补充建议

### 需要新增的文档
1. **docs/architecture.md** - 架构图 + 数据流
2. **docs/troubleshooting.md** - 常见问题排查
3. **CONTRIBUTING.md** - 贡献指南
4. **docs/deployment.md** - 持续补充生产部署检查清单

### 需要更新的文档
1. **README.md** - 添加测试运行说明
2. **CLAUDE.md** - 补充测试策略和已知限制

---

## 🎓 技术栈建议

### 可以考虑引入的工具
| 工具 | 用途 | 优先级 | 理由 |
|-----|------|--------|------|
| **ruff** | Python linter | 🔴 高 | 比 pylint 快100倍 |
| **mypy** | 类型检查 | 🔴 高 | 已有类型标注，差最后一步 |
| **Alembic** | 数据库迁移 | 🟡 中 | 替代手动 schema 迁移 |
| **Sentry** | 错误追踪 | 🟢 低 | 生产环境必备，开发环境可选 |
| **Grafana** | 监控面板 | 🟢 低 | 配合 Prometheus 使用 |

### 不建议引入的工具
- ❌ **复杂 ORM 抽象** (当前 SQLAlchemy 已足够)
- ❌ **Redux** (前端状态管理，过度设计)
- ❌ **微服务拆分** (当前单体架构合理)

---

## 📈 成功指标

### 代码质量
- [ ] 测试覆盖率: 后端 > 80%, 前端 > 60%
- [ ] 类型检查: mypy 0错误
- [ ] Linter: ruff 0警告

### 性能基线
- [ ] API P95 响应时间 < 500ms
- [ ] RAG 检索 < 200ms
- [ ] 前端首屏 < 2s

### 可靠性
- [ ] CI 通过率 > 99%
- [ ] 生产错误率 < 0.1%
- [ ] 服务可用性 > 99.9%

---

## 🤝 下一步行动

**建议优先级排序**:
1. 🔴 添加 ruff + mypy (防止新bug)
2. 🟡 前端核心测试 (保护关键路径)
3. 🟡 环境变量验证 (防止配置错误)
4. 🟡 API metrics 与性能基线
5. 🟢 Docker 多阶段构建 (优化部署)

**预估工作量**: 3-5个工作日完成前3项

---

*本文档会随着项目演进持续更新*
