# 可视化数据监控面板 - 后端

FastAPI 后端服务，支持文件上传、数据去重、JWT 认证。

## 一键部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?templateId=&templateUrl=https://github.com/Morethanbetter/ev-charge-dashboard)

> **注意**：部署后需手动添加 PostgreSQL 插件并配置环境变量（见下方说明）。

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

### 方式一：一键部署（推荐）

1. 点击上方 "Deploy on Railway" 按钮
2. Railway 会自动创建项目并识别 `backend/railway.toml`
3. 添加 PostgreSQL 插件：在 Railway Dashboard 中点击 "New" -> "Database" -> "PostgreSQL"
4. 配置环境变量（见下方表格）
5. 部署完成后访问 Railway 分配的域名

### 方式二：手动部署

1. 在 [Railway](https://railway.app) 创建新项目
2. 从 GitHub 仓库导入，Root Directory 设为 `backend`
3. 添加 PostgreSQL 插件
4. 配置环境变量
5. Railway 自动检测 `railway.toml` 并部署

### 环境变量配置

| 变量 | 说明 | 获取方式 |
|------|------|----------|
| DATABASE_URL | PostgreSQL 连接串 | Railway PostgreSQL 插件自动生成 |
| SECRET_KEY | JWT 密钥（生产环境请使用随机字符串） | 自行生成：`openssl rand -hex 32` |
| PORT | 服务端口 | Railway 自动设置，无需手动配置 |
| MAX_FILE_SIZE | 最大文件大小 (bytes) | 默认 52428800 (50MB) |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间 (分钟) | 默认 120 |

### 健康检查

部署后访问 `/api/v1/health` 验证服务状态。

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

> **安全提示**：生产环境请务必修改默认密码和 SECRET_KEY。
