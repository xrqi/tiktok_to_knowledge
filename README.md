# 短视频知识提炼工具

一个自动化工具，可以从抖音、快手等短视频平台提取视频内容，通过AI分析提炼知识点，并提供知识管理和复习功能。

## 功能特性

- **多平台视频获取**：支持从抖音、快手等平台下载视频
- **语音转文字**：自动提取视频音频并转换为文本
- **AI知识分析**：使用大语言模型提取知识点、生成摘要和分类
- **知识管理**：结构化存储知识点，支持搜索和标签管理
- **智能复习**：基于间隔重复算法的知识复习系统
- **桌面GUI界面**：直观易用的桌面应用程序
- **系统监控**：实时监控系统资源使用情况

## 系统要求

- Python 3.8+
- ffmpeg（用于视频处理）
- 网络连接（用于下载视频和AI分析）

## 安装步骤

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

## 使用方法

### 1. 直接运行GUI界面

```bash
python main_window.py
```

### 2. 命令行部署

```bash
python deploy.py local
```

### 3. 使用Docker部署（可选）

```bash
# 构建Docker镜像
docker build -t video-knowledge-extractor .

# 运行容器
docker run -d -v ./data:/app/data video-knowledge-extractor
```

## 项目结构

```
douyin_ks_to_knowledge/
├── config.py          # 配置管理
├── database_init.py   # 数据库初始化
├── video_acquisition.py  # 视频获取模块
├── video_processing.py   # 视频处理模块
├── ai_analysis.py     # AI分析模块
├── knowledge_manager.py  # 知识管理模块
├── main_window.py     # 主界面GUI
├── system_monitor.py  # 系统监控
├── logging_config.py  # 日志配置
├── deploy.py         # 部署脚本
├── requirements.txt   # 依赖列表
└── README.md         # 本文件
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

## API接口

本项目主要为桌面应用程序，但核心功能模块可作为库导入使用：

```python
from video_acquisition import VideoAcquisition
from video_processing import VideoProcessor
from ai_analysis import AIAnalyzer
from knowledge_manager import KnowledgeManager
```

## 数据库结构

系统使用SQLite数据库存储以下信息：
- 视频信息表 (videos)
- 转录文本表 (transcripts)
- 知识条目表 (knowledge)
- 复习记录表 (review_records)
- 配置表 (config)

## 隐私和安全

- 所有数据本地存储，不上传到任何服务器
- API密钥仅在本地使用，不会被记录到日志中
- 支持离线AI模型部署

## 开发

### 运行测试

```bash
python -m pytest tests/
```

### 代码格式化

```bash
black .
```

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

[请在此处添加许可证信息]

## 常见问题

1. **视频下载失败**：检查网络连接和视频URL是否正确
2. **语音识别错误**：确保音频质量良好，可尝试不同Whisper模型
3. **AI分析失败**：检查API密钥配置和网络连接
4. **GUI界面无响应**：长时间处理时界面会暂时无响应，处理完成后会恢复

## 技术支持

如有问题，请创建Issue或联系项目维护者。