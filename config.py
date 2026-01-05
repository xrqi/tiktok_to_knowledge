import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass

@dataclass
class VideoConfig:
    """视频处理配置"""
    max_download_concurrent: int = 3
    download_timeout: int = 60
    video_quality: str = "720p"
    temp_dir: str = "./temp"
    download_dir: str = "./downloads"

@dataclass
class AIConfig:
    """AI分析配置"""
    provider: str = "deepseek"  # openai, anthropic, local, deepseek
    model: str = "deepseek-chat"
    api_key: Optional[str] = "sk-c6e80ce9dd414036afc8827868aa9a6f"
    temperature: float = 0.3
    max_tokens: int = 2000
    chunk_size: int = 1000

@dataclass
class DatabaseConfig:
    """数据库配置"""
    db_path: str = "./data/knowledge.db"
    backup_dir: str = "./data/backup"
    max_backup_files: int = 5

@dataclass
class AppConfig:
    """应用配置"""
    debug: bool = False
    log_level: str = "INFO"
    data_dir: str = "./data"
    max_workers: int = 4
    ui_theme: str = "light"

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则创建默认配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
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
                "api_key": os.getenv("AI_API_KEY", ""),
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
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置值，支持点分路径，如 'ai.provider'"""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """设置配置值，支持点分路径"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def get_video_config(self) -> VideoConfig:
        """获取视频配置"""
        video_config = self.get("video", {})
        return VideoConfig(
            max_download_concurrent=video_config.get("max_download_concurrent", 3),
            download_timeout=video_config.get("download_timeout", 60),
            video_quality=video_config.get("video_quality", "720p"),
            temp_dir=video_config.get("temp_dir", "./temp"),
            download_dir=video_config.get("download_dir", "./downloads")
        )
    
    def get_ai_config(self) -> AIConfig:
        """获取AI配置"""
        ai_config = self.get("ai", {})
        return AIConfig(
            provider=ai_config.get("provider", "openai"),
            model=ai_config.get("model", "gpt-3.5-turbo"),
            api_key=ai_config.get("api_key") or os.getenv("AI_API_KEY"),
            temperature=ai_config.get("temperature", 0.3),
            max_tokens=ai_config.get("max_tokens", 2000),
            chunk_size=ai_config.get("chunk_size", 1000)
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        db_config = self.get("database", {})
        return DatabaseConfig(
            db_path=db_config.get("db_path", "./data/knowledge.db"),
            backup_dir=db_config.get("backup_dir", "./data/backup"),
            max_backup_files=db_config.get("max_backup_files", 5)
        )
    
    def get_app_config(self) -> AppConfig:
        """获取应用配置"""
        app_config = self.get("app", {})
        return AppConfig(
            debug=app_config.get("debug", False),
            log_level=app_config.get("log_level", "INFO"),
            data_dir=app_config.get("data_dir", "./data"),
            max_workers=app_config.get("max_workers", 4),
            ui_theme=app_config.get("ui_theme", "light")
        )

# 全局配置管理器实例
config_manager = ConfigManager()