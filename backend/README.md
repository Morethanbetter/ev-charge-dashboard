# 可视化数据监控面板 - 后端

FastAPI 后端服务，支持文件上传、数据去重、JWT 认证。

## 技术栈

- 框架: FastAPI + Uvicorn
- 数据库: PostgreSQL 16 (asyncpg)
- ORM: SQLAlchemy 2.0 (async)
- 认证: JWT (HS256)
- 容器化: Docker + Nginx 负载均衡

## 本地开发

1. 复制环境变量: cp .env.example .env
2. 启动服务: ./deploy.sh

服务地址:
- 前端: http://localhost
- API (Nginx LB): http://localhost/api/
- Swagger 文档: http://localhost:8000/docs

默认账号: admin / admin123

## 架构

Nginx (:80)
  /     -> 前端静态资源
  /api/ -> upstream backend (round-robin)
            app1:8000
            app2:8000
            app3:8000
              |
          PostgreSQL (:5432)

## Railway 部署

1. 在 Railway 创建新项目
2. 添加 PostgreSQL 插件
3. 连接 GitHub 仓库，Root Directory 设为 backend
4. 设置环境变量：
   - DATABASE_URL = Railway 自动生成的 PostgreSQL 连接串
   - SECRET_KEY = 你的密钥
5. Railway 自动检测 railway.toml 并部署

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接串 | - |
| SECRET_KEY | JWT 密钥 | - |
| PORT | 服务端口 | 8000 |
| MAX_FILE_SIZE | 最大文件大小 (bytes) | 52428800 |
