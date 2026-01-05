import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

class DeploymentManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.downloads_dir = self.project_root / "downloads"
        self.temp_dir = self.project_root / "temp"
        self.logs_dir = self.project_root / "logs"
    
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.config_dir,
            self.data_dir,
            self.downloads_dir,
            self.temp_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"创建目录: {directory}")
    
    def install_dependencies(self):
        """安装依赖包"""
        requirements_file = self.project_root / "requirements.txt"
        
        if requirements_file.exists():
            print("正在安装依赖包...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
                print("依赖包安装完成")
            except subprocess.CalledProcessError as e:
                print(f"依赖包安装失败: {e}")
                sys.exit(1)
        else:
            print("未找到requirements.txt文件")
    
    def setup_config(self):
        """设置配置文件"""
        config_file = self.project_root / "config.json"
        
        if not config_file.exists():
            default_config = {
                "video": {
                    "max_download_concurrent": 3,
                    "download_timeout": 60,
                    "video_quality": "720p",
                    "temp_dir": "./temp",
                    "download_dir": "./downloads"
                },
                "ai": {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "api_key": "",
                    "temperature": 0.3,
                    "max_tokens": 2000,
                    "chunk_size": 1000
                },
                "database": {
                    "db_path": "./data/knowledge.db",
                    "backup_dir": "./data/backup",
                    "max_backup_files": 5
                },
                "app": {
                    "debug": False,
                    "log_level": "INFO",
                    "data_dir": "./data",
                    "max_workers": 4,
                    "ui_theme": "light"
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"创建默认配置文件: {config_file}")
        else:
            print("配置文件已存在")
    
    def setup_database(self):
        """初始化数据库"""
        from database_init import DatabaseManager
        db_manager = DatabaseManager()
        db_manager.init_database()
        print("数据库初始化完成")
    
    def deploy(self, target: str = "local"):
        """执行部署"""
        print("开始部署短视频知识提炼工具...")
        
        if target == "local":
            self.create_directories()
            self.install_dependencies()
            self.setup_config()
            self.setup_database()
            print("本地部署完成!")
        elif target == "docker":
            print("Docker部署需要先构建镜像...")
            # Docker部署逻辑将在Dockerfile中处理
            self.create_directories()
            self.setup_config()
            self.setup_database()
            print("Docker部署准备完成!")
        elif target == "systemd":
            self.create_directories()
            self.install_dependencies()
            self.setup_config()
            self.setup_database()
            self.setup_systemd_service()
            print("Systemd服务部署完成!")
    
    def setup_systemd_service(self):
        """设置systemd服务（仅限Linux）"""
        if os.name != 'posix':
            print("Systemd服务仅支持Linux系统")
            return
        
        service_content = f"""[Unit]
Description=短视频知识提炼工具
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={self.project_root}
ExecStart={sys.executable} {self.project_root / 'main.py'}
Restart=always
Environment=PYTHONPATH={self.project_root}

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/video-knowledge-extractor.service")
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            print(f"Systemd服务文件已创建: {service_file}")
            print("运行以下命令启用服务:")
            print("sudo systemctl daemon-reload")
            print("sudo systemctl enable video-knowledge-extractor.service")
            print("sudo systemctl start video-knowledge-extractor.service")
        except PermissionError:
            print(f"权限不足，无法创建服务文件: {service_file}")
            print("请以root权限运行此脚本或手动创建服务文件")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="短视频知识提炼工具部署脚本")
    parser.add_argument("target", nargs="?", default="local", 
                       choices=["local", "docker", "systemd"],
                       help="部署目标: local, docker, 或 systemd")
    
    args = parser.parse_args()
    
    deploy_manager = DeploymentManager()
    deploy_manager.deploy(args.target)