from src.core.database_init import DatabaseManager

db = DatabaseManager()
db.init_database()

# 检查表是否创建成功
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("数据库表:")
for row in cursor.fetchall():
    print(f"  {row[0]}")

conn.close()

print("\n数据库初始化完成")
