# 代码结构迁移指南

本文档说明如何从旧的代码结构迁移到新的模块化结构。

## 迁移概述

新的代码结构将项目分为三个主要模块：
- `src/core/` - 核心功能模块
- `src/ui/` - 用户界面模块
- `src/utils/` - 工具模块

## 迁移步骤

### 1. 更新导入路径

所有Python文件的导入语句需要更新为新的路径格式：

#### 旧格式：
```python
from video_acquisition import VideoAcquisition
from video_processing import VideoProcessor
from ai_analysis import AIAnalyzer
from knowledge_manager import KnowledgeManager
from database_init import DatabaseManager
from config import config_manager
```

#### 新格式：
```python
from src.core.video_acquisition import VideoAcquisition
from src.core.video_processing import VideoProcessor
from src.core.ai_analysis import AIAnalyzer
from src.core.knowledge_manager import KnowledgeManager
from src.core.database_init import DatabaseManager
from src.core.config import config_manager
```

### 2. 更新启动命令

#### 旧命令：
```bash
python main_window.py
python web_app.py
python cli.py
```

#### 新命令：
```bash
python src/ui/main_window.py
python src/ui/web_app.py
python src/ui/cli.py
```

或者使用启动脚本：
```bash
# Windows
start.bat

# Linux/Mac
bash start.sh
```

### 3. 更新Docker配置

Dockerfile和docker-compose.yml已经更新，主要变化：

#### Dockerfile:
```dockerfile
ENV FLASK_APP=src/ui/web_app.py
ENV PYTHONPATH=/app
CMD ["python", "src/ui/web_app.py", "--host", "0.0.0.0", "--port", "5000"]
```

#### docker-compose.yml:
```yaml
volumes:
  - ./src:/app/src  # 挂载整个src目录
environment:
  - FLASK_APP=src/ui/web_app.py
  - PYTHONPATH=/app
```

### 4. 更新工具脚本

维护工具脚本的导入路径也需要更新：

#### 旧格式：
```python
from database_init import DatabaseManager
```

#### 新格式：
```python
from src.core.database_init import DatabaseManager
```

## 文件映射表

| 旧位置 | 新位置 |
|--------|--------|
| `config.py` | `src/core/config.py` |
| `logging_config.py` | `src/core/logging_config.py` |
| `database_init.py` | `src/core/database_init.py` |
| `video_acquisition.py` | `src/core/video_acquisition.py` |
| `video_processing.py` | `src/core/video_processing.py` |
| `ai_analysis.py` | `src/core/ai_analysis.py` |
| `knowledge_manager.py` | `src/core/knowledge_manager.py` |
| `douyin_login.py` | `src/core/douyin_login.py` |
| `system_monitor.py` | `src/core/system_monitor.py` |
| `main_window.py` | `src/ui/main_window.py` |
| `cli.py` | `src/ui/cli.py` |
| `web_app.py` | `src/ui/web_app.py` |
| `export_manager.py` | `src/utils/export_manager.py` |
| `mind_map_generator.py` | `src/utils/mind_map_generator.py` |
| `rebuild_fts.py` | `tools/rebuild_fts.py` |
| `reinit_db.py` | `tools/reinit_db.py` |
| `reset_db.py` | `tools/reset_db.py` |

## 已删除的文件

以下文件已被删除或移动：

- `add_sample_data.py` - 测试用脚本（已删除）
- `get_video_urls.py` - 简单查询脚本（已删除）
- `monitor_task.py` - 测试用脚本（已删除）
- `manual_login.py` - 功能已集成到douyin_login.py（已删除）
- `IMPLEMENTATION_PLAN.md` - 开发文档（已删除）
- `knowledge_base.db` - 旧数据库（已删除）
- `start-docker.bat` - 功能重复（已删除）
- `deploy.py` - 部署管理器（可选，已移动到src/utils/）

## 验证迁移

迁移完成后，请验证以下功能：

1. **GUI界面**
   ```bash
   python src/ui/main_window.py
   ```

2. **Web界面**
   ```bash
   python src/ui/web_app.py
   ```
   访问 http://localhost:5000

3. **命令行界面**
   ```bash
   python src/ui/cli.py --help
   ```

4. **Docker部署**
   ```bash
   docker-compose up -d
   ```

## 常见问题

### Q: 导入错误 "ModuleNotFoundError"

A: 确保使用新的导入路径，并且Python路径包含项目根目录。可以设置环境变量：
```bash
export PYTHONPATH=/path/to/project:$PYTHONPATH  # Linux/Mac
set PYTHONPATH=E:\PythonProjects\douyin_ks_to_knowledge  # Windows
```

### Q: Docker容器启动失败

A: 检查Dockerfile和docker-compose.yml中的路径是否正确更新。确保`PYTHONPATH`环境变量已设置。

### Q: 旧脚本无法运行

A: 更新脚本中的导入路径，参考上面的"文件映射表"。

## 回滚

如果需要回滚到旧结构，可以使用Git恢复：

```bash
git checkout HEAD~1 -- .
```

或者手动将文件从`src/`目录移回根目录，并更新所有导入路径。

## 联系支持

如果遇到迁移问题，请：
1. 检查本文档的"常见问题"部分
2. 查看项目README.md
3. 提交Issue到项目仓库
