import sqlite3

def rebuild_fts_table():
    conn = sqlite3.connect('./data/knowledge.db')
    cursor = conn.cursor()
    
    print("=== 重建FTS表 ===\n")
    
    # 删除旧的FTS表
    print("1. 删除旧的FTS表...")
    cursor.execute("DROP TABLE IF EXISTS knowledge_fts")
    conn.commit()
    print("   完成\n")
    
    # 创建新的FTS表（使用trigram分词器）
    print("2. 创建新的FTS表（使用trigram分词器）...")
    cursor.execute("""
        CREATE VIRTUAL TABLE knowledge_fts 
        USING fts5(title, content, tags, content_rowid='id', tokenize='trigram')
    """)
    conn.commit()
    print("   完成\n")
    
    # 重新填充FTS表
    print("3. 重新填充FTS表...")
    cursor.execute("SELECT id, title, content, tags FROM knowledge")
    knowledge_items = cursor.fetchall()
    
    for item in knowledge_items:
        knowledge_id, title, content, tags = item
        cursor.execute("""
            INSERT INTO knowledge_fts (rowid, title, content, tags)
            VALUES (?, ?, ?, ?)
        """, (knowledge_id, title, content, tags))
    
    conn.commit()
    print(f"   已填充 {len(knowledge_items)} 条记录\n")
    
    # 测试搜索
    print("4. 测试搜索功能...")
    test_queries = [
        '机器学习',
        '监督学习',
        '无监督学习',
        'Python',
        'Web开发',
        '前端',
        '后端',
    ]
    
    for query in test_queries:
        print(f"   搜索 '{query}':")
        cursor.execute("""
            SELECT k.id, k.title, k.category
            FROM knowledge k
            WHERE k.id IN (
                SELECT rowid FROM knowledge_fts
                WHERE knowledge_fts MATCH ?
            )
        """, (query,))
        results = cursor.fetchall()
        print(f"   结果数量: {len(results)}")
        for row in results:
            print(f"   - [{row[0]}] {row[1]} ({row[2]})")
        print()
    
    conn.close()
    print("=== FTS表重建完成 ===")

if __name__ == '__main__':
    rebuild_fts_table()
