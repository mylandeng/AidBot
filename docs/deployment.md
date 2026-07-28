# AidBot 部署指南

AidBot 的本地开发配置和生产配置是分开的：

- `docker-compose.yml`、`backend/Dockerfile`、`frontend/Dockerfile`：本地开发，保留源码挂载和热更新。
- `docker-compose.prod.yml`、`backend/Dockerfile.prod`、`frontend/Dockerfile.prod`：生产部署，不挂载源码，前端使用构建后的 `next start`，后端不启用 reload。

两个镜像分别使用 `backend/` 和 `frontend/` 作为 Docker 构建上下文。对应目录下的 `.dockerignore` 会排除虚拟环境、依赖目录、构建缓存、日志和本地环境变量，避免无关文件进入构建上下文。新增本地缓存或工具输出目录时，也应同步检查对应的 `.dockerignore`。

## 本地开发

现有用法不变：

```powershell
Copy-Item .env.example .env
docker compose up -d --build
```

访问：

- 前端：<http://localhost:3010>
- 后端健康检查：<http://localhost:8010/health>

## 构建生产镜像

先复制生产变量模板并填写真实值：

```powershell
Copy-Item .env.prod.example .env.prod
```

至少修改：

- `AUTH_SECRET_KEY`
- `SEED_ADMIN_PASSWORD`
- `POSTGRES_PASSWORD`
- `BACKEND_CORS_ORIGINS`
- `NEXT_PUBLIC_API_BASE_URL`
- `LLM_API_KEY`（如果使用外部模型）

如果服务器使用镜像仓库，直接拉取并启动：

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

生产 Compose 只负责运行已经构建好的镜像，不要求服务器存在 `backend/`、`frontend/` 源码目录。镜像由 GitHub Actions 或本地 `docker build` 生成。

停止服务但保留数据库数据：

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml down
```

不要使用 `down -v`，否则会删除 PostgreSQL 数据卷。

## 推送到镜像仓库

### 使用 GitHub Actions 自动构建

项目中的 `.github/workflows/docker-publish.yml` 会在推送到 `main` 后自动构建并推送两个镜像到 GitHub Container Registry：

```text
ghcr.io/mylandeng/aidbot-backend:latest
ghcr.io/mylandeng/aidbot-frontend:latest
```

工作流使用内置的 `GITHUB_TOKEN` 登录 GHCR，不需要额外创建个人 Token。前端镜像不再在构建时写死后端地址，浏览器访问的后端地址由部署服务器上的 `.env.prod` 在容器启动时注入。

推送代码后，可以在仓库的 `Actions` 页面查看构建结果。构建成功后，同事服务器上的 `.env.prod` 至少需要使用对应镜像：

```env
BACKEND_IMAGE=ghcr.io/mylandeng/aidbot-backend:latest
FRONTEND_IMAGE=ghcr.io/mylandeng/aidbot-frontend:latest
NEXT_PUBLIC_API_BASE_URL=https://api-aidbot.example.com
API_INTERNAL_BASE_URL=http://backend:8010
```

其中 `NEXT_PUBLIC_API_BASE_URL` 必须是用户浏览器能够访问的后端公网地址；`API_INTERNAL_BASE_URL` 是前端容器访问后端容器的内部地址，默认使用 `http://backend:8010`。

如果仓库或镜像包是私有的，同事需要先登录：

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

数据库镜像仍然使用官方的 `pgvector/pgvector:pg16`，不由本工作流重新构建。

### 手动推送到其他镜像仓库

把 `.env.prod` 中的镜像名改为公司镜像仓库地址，例如：

```env
BACKEND_IMAGE=registry.example.com/aidbot/backend:2026-07-23
FRONTEND_IMAGE=registry.example.com/aidbot/frontend:2026-07-23
```

然后在有源码的构建机上执行：

```powershell
docker build -t registry.example.com/aidbot/backend:2026-07-23 -f backend/Dockerfile.prod backend
docker build -t registry.example.com/aidbot/frontend:2026-07-23 -f frontend/Dockerfile.prod --build-arg API_INTERNAL_BASE_URL=http://backend:8010 frontend
docker push registry.example.com/aidbot/backend:2026-07-23
docker push registry.example.com/aidbot/frontend:2026-07-23
```

同事服务器上准备同版本的 `.env.prod` 后执行：

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

## 生产注意事项

1. `NEXT_PUBLIC_API_BASE_URL` 由前端容器启动脚本写入 `/runtime-config.js`，修改 `.env.prod` 后需要重建容器或强制重启 frontend，但不需要重新构建前端镜像。
2. `BACKEND_CORS_ORIGINS` 必须填写实际前端域名，多个域名用逗号分隔。
3. 当前生产 Compose 默认使用带持久化卷的 pgvector 容器。云上正式环境也可以把 `DATABASE_URL` 替换成带 pgvector 扩展的托管 PostgreSQL。
4. 数据库端口没有映射到宿主机公网，只通过 Compose 内部网络给 backend 使用。
5. 建议在云端前面配置 HTTPS 反向代理，并将前端、后端域名分别转发到 `3010`、`8010`。
6. 如果服务器使用旧版 `docker-compose`（例如 1.25.0），请把 `.env.prod` 复制为 Compose 文件同目录下的 `.env`，然后使用 `docker-compose -f docker-compose.prod.yml up -d --no-build`；生产 Compose 使用兼容健康检查依赖的 `version: "2.4"`，并避免使用旧版本不支持的变量默认值和错误提示插值语法。

验证前端镜像是否支持运行时切换后端地址：

```powershell
docker run --rm `
  -e NEXT_PUBLIC_API_BASE_URL=http://test-server.example:8010 `
  --entrypoint /bin/sh `
  registry.example.com/aidbot/frontend:2026-07-23 `
  -c "./docker-entrypoint.sh true && cat /app/public/runtime-config.js"
```

输出中的 `apiBaseUrl` 应该等于当前命令传入的 `NEXT_PUBLIC_API_BASE_URL`。
