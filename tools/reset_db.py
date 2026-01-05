import sqlite3
import os

# 删除旧的数据库
if os.path.exists('data/knowledge.db'):
    os.remove('data/knowledge.db')
    print("已删除旧数据库")

# 重新初始化数据库
from src.core.database_init import DatabaseManager
db = DatabaseManager()
db.init_database()

print("数据库重新初始化完成")
