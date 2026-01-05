import logging
import logging.config
import os
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别，可选 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        log_file: 日志文件路径，如果为None则只输出到控制台
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 如果没有指定日志文件，则使用默认文件名
    if log_file is None:
        log_file = log_dir / "app.log"
    
    # 日志配置字典
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'level': 'DEBUG',  # 文件记录所有级别的日志
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'detailed',
                'filename': str(log_file),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            '': {  # 根日志记录器
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'video_extractor': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'knowledge_manager': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'ai_analysis': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            },
            'database': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False
            }
        }
    }
    
    # 应用日志配置
    logging.config.dictConfig(logging_config)
    
    # 设置第三方库的日志级别以减少噪音
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


# 预定义的日志记录器
app_logger = get_logger('video_extractor')
knowledge_logger = get_logger('knowledge_manager')
ai_logger = get_logger('ai_analysis')
db_logger = get_logger('database')


if __name__ == "__main__":
    # 测试日志配置
    setup_logging(log_level="DEBUG")
    
    logger = get_logger(__name__)
    logger.debug("调试信息")
    logger.info("普通信息")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误")