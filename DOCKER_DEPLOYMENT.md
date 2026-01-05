# Docker 部署指南

本文档介绍如何使用 Docker 部署知识管理系统。

## 前置要求

- Docker (版本 20.10 或更高)
- Docker Compose (版本 1.29 或更高)

## 快速开始

### 1. 构建并运行容器

使用 Docker Compose（推荐）：

```bash
docker-compose up -d
```

或者使用 Docker 命令：

```bash
# 构建镜像
docker build -t knowledge-app .

# 运行容器
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/logs:/app/logs \
  --name knowledge-app \
  knowledge-app
```

### 2. 访问应用

打开浏览器访问：http://localhost:5000

## 配置说明

### 环境变量

在 `docker-compose.yml` 中可以配置以下环境变量：

- `FLASK_ENV`: 运行环境（production/development）
- `FLASK_APP`: Flask 应用入口文件

### 端口映射

默认映射端口为 5000，如需修改：

```yaml
ports:
  - "8080:5000"  # 将容器5000端口映射到主机8080端口
```

### 数据持久化

以下目录通过 volume 挂载实现数据持久化：

- `/app/data`: 数据库文件
- `/app/downloads`: 下载的视频和音频文件
- `/app/logs`: 应用日志

## 常用命令

### 查看容器状态

```bash
docker-compose ps
```

### 查看日志

```bash
docker-compose logs -f web
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 进入容器

```bash
docker-compose exec web bash
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

## 生产环境部署

### 1. 使用 Nginx 反向代理

创建 `nginx.conf`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

使用 Docker Compose 运行 Nginx：

```yaml
version: '3.8'

services:
  web:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./downloads:/app/downloads
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
    expose:
      - "5000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - web
```

### 2. 配置 HTTPS

使用 Let's Encrypt 和 Certbot：

```bash
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --standalone -d your-domain.com
```

### 3. 健康检查

容器已配置健康检查，默认每30秒检查一次：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## 故障排查

### 容器无法启动

查看日志：

```bash
docker-compose logs web
```

### 端口冲突

修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8080:5000"  # 修改为其他端口
```

### 权限问题

确保挂载的目录有正确的权限：

```bash
chmod -R 755 data downloads logs
```

### 数据库问题

如果数据库损坏，可以删除并重新创建：

```bash
# 停止容器
docker-compose down

# 删除数据库文件
rm -f data/knowledge.db

# 重新启动
docker-compose up -d
```

## 性能优化

### 1. 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  web:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### 2. 使用多阶段构建

优化镜像大小（已在 Dockerfile 中实现）。

### 3. 缓存依赖

Docker 会自动缓存依赖安装层，加速后续构建。

## 备份与恢复

### 备份数据

```bash
# 备份数据库
docker-compose exec web cp /app/data/knowledge.db /app/data/backup_$(date +%Y%m%d).db

# 备份所有数据
tar -czf backup_$(date +%Y%m%d).tar.gz data downloads logs
```

### 恢复数据

```bash
# 停止容器
docker-compose down

# 恢复数据
tar -xzf backup_20240101.tar.gz

# 启动容器
docker-compose up -d
```

## 安全建议

1. **不要在镜像中包含敏感信息**：使用环境变量或 secrets 管理敏感配置
2. **定期更新基础镜像**：`docker pull python:3.11-slim`
3. **限制容器权限**：使用非 root 用户运行（可选）
4. **配置防火墙**：只开放必要的端口
5. **启用 HTTPS**：使用 SSL/TLS 加密通信

## 监控与日志

### 查看资源使用

```bash
docker stats knowledge-app
```

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f web

# 限制日志大小
docker-compose down
docker-compose up -d --log-opt max-size=10m --log-opt max-file=3
```

## 更新日志

- 2024-01-01: 初始版本
- 添加 Docker Compose 配置
- 添加健康检查
- 优化镜像大小
