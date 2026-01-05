# 短视频知识提炼工具

一个自动化工具，可以从抖音、快手等短视频平台提取视频内容，通过AI分析提炼知识点，并提供知识管理和复习功能。

## 功能特性

### 核心功能
- **多平台视频获取**：支持从抖音、快手等平台下载视频
- **语音转文字**：自动提取视频音频并转换为文本
- **AI知识分析**：使用大语言模型提取知识点、生成摘要和分类
- **知识管理**：结构化存储知识点，支持搜索和标签管理
- **智能复习**：基于间隔重复算法的知识复习系统

### 新增功能
- **Web界面**：基于Flask的现代化Web应用
  - 知识列表展示（分页）
  - 知识搜索（支持全文搜索）
  - 视频导入（实时进度显示）
  - 知识编辑和删除
  - 抖音跳转按钮（直接跳转到原视频）
  - 统计信息展示（视频数、知识数等）

- **知识图谱**：可视化知识关联关系
  - 力导向图布局
  - 多种节点类型（知识、分类、标签、视频）
  - 节点交互（拖拽、缩放、点击查看详情）
  - 关联关系展示（分类、标签、来源视频、共同标签）

- **Docker部署**：容器化部署方案
  - 一键启动Web服务
  - 数据持久化存储
  - 环境变量配置
  - 健康检查机制

- **桌面GUI界面**：直观易用的桌面应用程序
- **系统监控**：实时监控系统资源使用情况

## 系统要求

### 基础要求
- Python 3.8+
- ffmpeg（用于视频处理）
- 网络连接（用于下载视频和AI分析）

### Web部署要求
- Docker（推荐）
- 2GB+ 可用内存
- 10GB+ 可用磁盘空间

## 安装步骤

### 方式一：本地运行

1. 克隆项目到本地：
   ```bash
   git clone <repository-url>
   cd douyin_ks_to_knowledge
   ```

2. 安装Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 安装系统依赖（ffmpeg）：
   - Windows: 使用Chocolatey `choco install ffmpeg` 或从官网下载
   - macOS: 使用Homebrew `brew install ffmpeg`
   - Linux: 使用包管理器，如 `sudo apt install ffmpeg`

4. 配置AI服务（可选）：
   - 编辑 `config.json` 文件，添加你的OpenAI或Anthropic API密钥
   - 或设置环境变量 `AI_API_KEY`

5. 运行应用：
   ```bash
   # GUI界面
   python src/ui/main_window.py
   
   # Web界面
   python src/ui/web_app.py
   
   # 命令行界面
   python src/ui/cli.py --help
   ```

**或者使用启动脚本：**
- Windows: 双击 `start.bat` 或在命令行运行 `start.bat`
- Linux/Mac: 运行 `bash start.sh`

### 方式二：Docker部署（推荐）

1. 克隆项目：
   ```bash
   git clone <repository-url>
   cd douyin_ks_to_knowledge
   ```

2. 配置环境变量：
   - 复制 `.env.example` 到 `.env`
   - 编辑 `.env` 文件，设置 `OPENAI_API_KEY`

3. 启动服务：
   ```bash
   # 使用docker-compose（推荐）
   docker-compose up -d
   
   # 或使用docker run
   docker build -t douyin-ks-to-knowledge .
   docker run -d -p 5000:5000 -v ./data:/app/data douyin-ks-to-knowledge
   ```

4. 访问Web界面：
   - 打开浏览器访问：http://localhost:5000
   - 或使用部署脚本：
     - Windows: `docker-deploy.bat`
     - Linux/Mac: `bash docker-deploy.sh`

## 使用方法

### 1. Web界面使用

#### 主页功能
- **知识列表**：查看所有知识条目，支持分页浏览
- **搜索知识**：输入关键词搜索相关知识
- **导入视频**：粘贴抖音视频URL，自动分析并导入知识
- **知识图谱**：可视化查看知识之间的关联关系
- **统计信息**：查看系统数据统计

#### 知识管理
- **查看详情**：点击知识卡片查看完整内容
- **编辑知识**：修改知识标题、内容、分类、标签等
- **删除知识**：删除不需要的知识条目
- **跳转视频**：点击抖音按钮直接跳转到原视频

#### 知识图谱
- **节点类型**：
  - 🔵 知识节点（蓝色）
  - 🟣 分类节点（紫色）
  - 🟢 标签节点（绿色）
  - 🟠 视频节点（橙色）
- **交互操作**：
  - 拖拽节点调整位置
  - 滚轮缩放视图
  - 点击节点查看详细信息
  - 悬停显示节点信息

### 2. 桌面GUI使用

```bash
python src/ui/main_window.py
```

### 3. 命令行使用

```bash
# 导入视频
python src/ui/cli.py import <video-url>

# 列出知识
python src/ui/cli.py list

# 搜索知识
python src/ui/cli.py search <keyword>

# 查看统计
python src/ui/cli.py stats
```

### 4. 部署脚本

```bash
# 本地部署
python deploy.py local

# 远程部署
python deploy.py remote
```

## 项目结构

```
douyin_ks_to_knowledge/
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   ├── config.py             # 配置管理
│   │   ├── logging_config.py     # 日志配置
│   │   ├── database_init.py     # 数据库初始化
│   │   ├── video_acquisition.py  # 视频获取模块
│   │   ├── video_processing.py   # 视频处理模块
│   │   ├── ai_analysis.py        # AI分析模块
│   │   ├── knowledge_manager.py  # 知识管理模块
│   │   ├── douyin_login.py       # 抖音登录
│   │   └── system_monitor.py     # 系统监控
│   ├── ui/                       # 用户界面
│   │   ├── main_window.py        # 主界面GUI
│   │   ├── cli.py                # 命令行界面
│   │   └── web_app.py            # Web应用
│   └── utils/                    # 工具模块
│       ├── export_manager.py     # 知识导出
│       └── mind_map_generator.py # 思维导图生成
├── templates/                    # Web模板
│   ├── index.html               # 主页
│   └── graph.html              # 知识图谱
├── static/                      # 静态资源
│   ├── style.css               # 样式文件
│   └── douyin-icon.png         # 抖音图标
├── tools/                       # 维护工具
│   ├── rebuild_fts.py          # 重建FTS表
│   ├── reinit_db.py            # 重新初始化数据库
│   └── reset_db.py              # 重置数据库
├── data/                        # 数据目录（Docker挂载）
├── downloads/                   # 下载目录
├── logs/                        # 日志目录
├── config.json                  # 配置文件
├── douyin_cookies.json          # 抖音cookies
├── .env                         # 环境变量
├── requirements.txt             # 依赖列表
├── docker-compose.yml           # Docker编排配置
├── Dockerfile                   # Docker镜像构建
├── .dockerignore                # Docker忽略文件
├── docker-deploy.bat            # Windows部署脚本
├── docker-deploy.sh             # Linux/Mac部署脚本
├── DOCKER_DEPLOYMENT.md         # Docker部署文档
├── DOCKER_QUICKSTART.md         # Docker快速开始
└── README.md                    # 本文件
```

## 配置说明

### config.json 配置项

- `video`: 视频处理相关配置
  - `max_download_concurrent`: 最大并发下载数
  - `download_timeout`: 下载超时时间
  - `video_quality`: 视频质量
  - `temp_dir`: 临时文件目录
  - `download_dir`: 下载目录

- `ai`: AI服务相关配置
  - `provider`: AI服务提供商 (openai, anthropic, local)
  - `model`: 使用的模型
  - `api_key`: API密钥
  - `temperature`: 生成温度
  - `max_tokens`: 最大token数
  - `chunk_size`: 文本分块大小

- `database`: 数据库配置
  - `db_path`: 数据库文件路径
  - `backup_dir`: 备份目录
  - `max_backup_files`: 最大备份文件数

- `app`: 应用程序配置
  - `debug`: 调试模式
  - `log_level`: 日志级别
  - `data_dir`: 数据目录
  - `max_workers`: 最大工作线程数
  - `ui_theme`: UI主题

### 环境变量（Docker）

- `OPENAI_API_KEY`: OpenAI API密钥
- `FLASK_ENV`: Flask环境（production/development）
- `FLASK_APP`: Flask应用入口

## API接口

### Web API

- `GET /` - 主页
- `GET /graph` - 知识图谱页面
- `GET /api/knowledge` - 获取知识列表（支持分页）
- `GET /api/knowledge/<id>` - 获取单个知识详情
- `PUT /api/knowledge/<id>` - 更新知识
- `DELETE /api/knowledge/<id>` - 删除知识
- `GET /api/knowledge-graph` - 获取知识图谱数据
- `GET /api/stats` - 获取统计信息
- `POST /api/analyze` - 分析视频
- `GET /api/task/<task_id>` - 获取任务状态

### 核心模块API

```python
from src.core.video_acquisition import VideoAcquisition
from src.core.video_processing import VideoProcessor
from src.core.ai_analysis import AIAnalyzer
from src.core.knowledge_manager import KnowledgeManager
```

## 数据库结构

系统使用SQLite数据库存储以下信息：
- **videos**: 视频信息表
  - id, platform, video_id, title, author, url
  - duration, download_path, download_date, status, metadata

- **transcripts**: 转录文本表
  - id, video_id, content, language, created_at

- **knowledge**: 知识条目表
  - id, title, content, category, tags, importance
  - source_video_id, created_at, updated_at

- **review_records**: 复习记录表
  - id, knowledge_id, review_date, interval_days, next_review_date

- **config**: 配置表
  - key, value, updated_at

## 隐私和安全

- 所有数据本地存储，不上传到任何服务器
- API密钥仅在本地使用，不会被记录到日志中
- 支持离线AI模型部署
- Docker部署时注意保护 `.env` 文件

## 开发

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black .
```

### Web开发

```bash
# 启动开发服务器
python src/ui/web_app.py --debug

# 访问
http://localhost:5000
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

### 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

[请在此处添加许可证信息]

## 常见问题

### 视频相关
1. **视频下载失败**：检查网络连接和视频URL是否正确
2. **语音识别错误**：确保音频质量良好，可尝试不同Whisper模型
3. **视频信息获取失败**：确保已安装Playwright并配置好cookies

### AI分析相关
1. **AI分析失败**：检查API密钥配置和网络连接
2. **JSON解析错误**：AI返回的JSON格式错误，系统会自动重试

### Web界面相关
1. **无法访问**：检查Docker容器是否正常运行
2. **知识图谱不显示**：检查浏览器控制台是否有JavaScript错误
3. **进度条不更新**：检查任务状态API是否正常

### 部署相关
1. **Docker构建失败**：检查Dockerfile语法和依赖
2. **容器启动失败**：检查端口占用和配置文件
3. **数据丢失**：确保正确挂载数据卷

## 技术支持

如有问题，请创建Issue或联系项目维护者。

### 获取帮助

- 查看文档：[项目Wiki](#)
- 提交Issue：[GitHub Issues](#)
- 邮件联系：[维护者邮箱](mailto:#)

## 更新日志

### v2.0.0 (2026-01-06)
- ✨ 新增Web界面，支持知识管理、搜索、导入
- ✨ 新增知识图谱可视化功能
- ✨ 新增Docker容器化部署支持
- ✨ 新增抖音跳转按钮，快速访问原视频
- ✨ 改进知识关联逻辑，支持多种关系类型
- 🐛 修复数据库连接和并发问题
- 🐛 修复AI响应JSON解析错误
- 📝 更新文档，添加Web和Docker部署说明

### v1.0.0
- 🎉 初始版本发布
- ✨ 支持抖音、快手视频下载
- ✨ AI知识分析和提取
- ✨ 知识管理和复习系统
- ✨ 桌面GUI界面
