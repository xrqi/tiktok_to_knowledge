# Docker 部署快速指南

## 问题诊断

### 错误信息
```
unable to get image 'douyin_ks_to_knowledge-web': error during connect:
Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.51/images/...":
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### 原因分析
这个错误表明 **Docker Desktop 未运行**。

## 解决方案

### 步骤 1: 启动 Docker Desktop

1. **在 Windows 开始菜单中搜索 "Docker Desktop"**
2. **点击启动 Docker Desktop**
3. **等待 Docker 图标在系统托盘中变为绿色**（通常需要 1-2 分钟）
4. **确认 Docker 已启动**：
   - 在系统托盘中找到 Docker 图标（鲸鱼图标）
   - 图标应该是绿色且稳定的
   - 右键点击图标，选择 "Docker Desktop is running" 确认

### 步骤 2: 验证 Docker 运行状态

打开 PowerShell 或命令提示符，运行：

```powershell
docker info
```

如果看到 Docker 系统信息，说明 Docker 已成功运行。

### 步骤 3: 使用部署脚本

#### Windows 用户（推荐）

**选项 A: 使用批处理脚本（.bat）**
```powershell
docker-deploy.bat
```

**选项 B: 使用 PowerShell 脚本（.ps1）**
```powershell
# 如果遇到执行策略限制，先运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后运行脚本：
.\docker-deploy.ps1
```

#### Linux/Mac 用户

```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

### 步骤 4: 选择操作

在部署脚本菜单中选择：
- **选项 1**: 构建并启动容器
- **选项 9**: 查看 Docker 信息（如果需要诊断）

## 手动部署（如果脚本无法使用）

### 使用 Docker Compose

```powershell
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f web

# 停止容器
docker-compose down
```

### 使用 Docker 命令

```powershell
# 构建镜像
docker build -t knowledge-app .

# 运行容器
docker run -d -p 5000:5000 ^
  -v "%cd%/data:/app/data" ^
  -v "%cd%/downloads:/app/downloads" ^
  -v "%cd%/logs:/app/logs" ^
  --name knowledge-app ^
  knowledge-app

# 查看日志
docker logs -f knowledge-app

# 停止容器
docker stop knowledge-app
docker rm knowledge-app
```

## 常见问题

### 1. Docker Desktop 启动失败

**症状**: Docker Desktop 无法启动或一直卡在启动界面

**解决方案**:
1. 重启 Docker Desktop
2. 检查 Windows 虚拟化是否启用：
   - 打开任务管理器 → 性能 → CPU
   - 确认 "虚拟化" 显示为 "已启用"
3. 检查 WSL2 是否安装：
   ```powershell
   wsl --list --verbose
   ```
4. 如果 WSL2 未安装，运行：
   ```powershell
   wsl --install
   ```

### 2. 端口 5000 被占用

**症状**: 启动容器时提示端口已被使用

**解决方案**:
1. 查找占用端口的进程：
   ```powershell
   netstat -ano | findstr :5000
   ```
2. 停止占用端口的进程，或修改端口映射：
   ```yaml
   # 在 docker-compose.yml 中修改
   ports:
     - "8080:5000"  # 使用 8080 端口
   ```

### 3. 权限问题

**症状**: 无法访问挂载的目录

**解决方案**:
```powershell
# 确保目录存在
mkdir data
mkdir downloads
mkdir logs

# 设置权限
icacls data /grant Everyone:F
icacls downloads /grant Everyone:F
icacls logs /grant Everyone:F
```

### 4. PowerShell 执行策略限制

**症状**: 运行 .ps1 脚本时提示无法加载

**解决方案**:
```powershell
# 临时允许执行
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 或永久允许当前用户执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. Docker 镜像构建失败

**症状**: 构建过程中出现错误

**解决方案**:
1. 检查网络连接
2. 清理 Docker 缓存：
   ```powershell
   docker system prune -a
   ```
3. 重新构建：
   ```powershell
   docker-compose build --no-cache
   ```

## 验证部署

### 1. 检查容器状态

```powershell
docker-compose ps
```

应该看到类似输出：
```
NAME                  STATUS         PORTS
douyin_ks_to_knowledge-web   Up             0.0.0.0:5000->5000/tcp
```

### 2. 访问应用

在浏览器中打开：http://localhost:5000

### 3. 查看日志

```powershell
docker-compose logs -f web
```

## 获取帮助

如果遇到其他问题：

1. 查看 Docker 日志：
   ```powershell
   docker logs knowledge-app
   ```

2. 查看 Docker Desktop 日志：
   - 右键点击系统托盘中的 Docker 图标
   - 选择 "Troubleshoot" → "Docker Desktop: Diagnose & Feedback"

3. 查看应用日志：
   ```powershell
   type logs\app.log
   ```

## 下一步

部署成功后，您可以：

1. 访问 Web 界面：http://localhost:5000
2. 导入视频进行分析
3. 搜索和管理知识库
4. 配置生产环境（参考 DOCKER_DEPLOYMENT.md）

## 相关文档

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 详细的部署文档
- [README.md](README.md) - 项目说明
- [docker-compose.yml](docker-compose.yml) - Docker Compose 配置
