# AidBot
专门给公司设计的售后问答系统。

## 本地开发

阶段 0 已提供可运行脚手架：

- `backend/`: FastAPI 后端，包含健康检查、基础路由和服务层边界。
- `frontend/`: Next.js 前端，包含基础工作台页面和 API 客户端。
- `docker-compose.yml`: PostgreSQL、后端、前端的本地开发栈。
- `.env.example`: 本地环境变量示例。
- `docs/api-contract.md`: 当前 API/数据合同草案。

### Docker 一键启动

```powershell
# 可选：需要覆盖默认环境变量时再复制
Copy-Item .env.example .env
docker compose up --build
```

启动后：

- 前端：http://localhost:3010
- 后端健康检查：http://localhost:8010/health
- 后端 API 文档：http://localhost:8010/docs

### 本机分别启动

后端：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

前端：

```powershell
cd frontend
npm install
npm run dev
```

默认前端通过 `NEXT_PUBLIC_API_BASE_URL=http://localhost:8010` 访问后端。

### 阶段 1 默认登录

本地开发默认账号：

- 邮箱：`admin@aidbot.local`
- 密码：`aidbot123`

这些值只用于本地阶段验证，部署前需要在 `.env` 中覆盖 `AUTH_SECRET_KEY`、`SEED_ADMIN_EMAIL` 和 `SEED_ADMIN_PASSWORD`。
