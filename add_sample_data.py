import sqlite3
from datetime import datetime
import json

def add_sample_data():
    conn = sqlite3.connect('./data/knowledge.db')
    cursor = conn.cursor()
    
    print("添加示例视频数据...")
    
    video_data = [
        ('douyin', 'video001', 'Python编程入门教程', '编程老师', 'https://example.com/video1', 600, './downloads/video1.mp4', 'completed'),
        ('douyin', 'video002', '机器学习基础概念', 'AI专家', 'https://example.com/video2', 800, './downloads/video2.mp4', 'completed'),
        ('douyin', 'video003', 'Web开发实战项目', '全栈工程师', 'https://example.com/video3', 1200, './downloads/video3.mp4', 'completed'),
    ]
    
    for data in video_data:
        cursor.execute("""
            INSERT OR IGNORE INTO videos 
            (platform, video_id, title, author, url, duration, download_path, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
    
    conn.commit()
    
    print("获取视频ID...")
    cursor.execute("SELECT id, title FROM videos")
    videos = cursor.fetchall()
    video_ids = {v[1]: v[0] for v in videos}
    
    print("添加示例转录文本...")
    transcripts = [
        (video_ids['Python编程入门教程'], 'Python是一种高级编程语言，具有简洁易读的语法。它可以用于Web开发、数据分析、人工智能等多个领域。Python拥有丰富的第三方库，如NumPy、Pandas、Django等。', 'zh'),
        (video_ids['机器学习基础概念'], '机器学习是人工智能的一个分支，它使计算机能够从数据中学习。主要类型包括监督学习、无监督学习和强化学习。常用的算法有线性回归、决策树、神经网络等。', 'zh'),
        (video_ids['Web开发实战项目'], 'Web开发包括前端和后端开发。前端技术有HTML、CSS、JavaScript，后端可以使用Python、Java、Node.js等。现代Web开发框架如React、Vue、Django等大大提高了开发效率。', 'zh'),
    ]
    
    for data in transcripts:
        cursor.execute("""
            INSERT OR IGNORE INTO transcripts 
            (video_id, content, language)
            VALUES (?, ?, ?)
        """, data)
    
    conn.commit()
    
    print("添加示例知识条目...")
    knowledge_data = [
        ('Python语言特点', 'Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。它的设计哲学强调代码的可读性和简洁的语法，尤其是使用空格缩进划分代码块，而非使用大括号或者关键词。', '编程语言', '["Python", "编程", "入门"]', video_ids['Python编程入门教程'], 5),
        ('Python应用领域', 'Python广泛应用于Web开发、数据分析、人工智能、科学计算、自动化运维等领域。在Web开发方面，Django和Flask是流行的框架；在数据科学方面，NumPy、Pandas和Matplotlib是核心库。', '应用领域', '["Python", "Web开发", "数据分析"]', video_ids['Python编程入门教程'], 4),
        ('监督学习', '监督学习是机器学习的一种方法，它使用标记的训练数据来学习从输入到输出的映射函数。常见的监督学习算法包括线性回归、逻辑回归、支持向量机、决策树和随机森林等。', '机器学习', '["监督学习", "算法", "分类"]', video_ids['机器学习基础概念'], 5),
        ('无监督学习', '无监督学习是一种机器学习方法，它使用未标记的数据来发现数据中的模式。主要技术包括聚类、降维和关联规则学习。K-means聚类和PCA降维是常用的无监督学习算法。', '机器学习', '["无监督学习", "聚类", "降维"]', video_ids['机器学习基础概念'], 4),
        ('前端开发技术', '前端开发涉及创建用户可见的网页界面。核心技术包括HTML用于结构，CSS用于样式，JavaScript用于交互。现代前端框架如React、Vue和Angular提供了组件化开发方式。', 'Web开发', '["前端", "HTML", "CSS", "JavaScript"]', video_ids['Web开发实战项目'], 5),
        ('后端开发技术', '后端开发处理服务器端的逻辑和数据管理。Python的Django和Flask、Java的Spring、Node.js的Express都是流行的后端框架。后端开发者需要掌握数据库管理、API设计和服务器部署等技能。', 'Web开发', '["后端", "API", "数据库"]', video_ids['Web开发实战项目'], 4),
    ]
    
    for data in knowledge_data:
        cursor.execute("""
            INSERT OR IGNORE INTO knowledge 
            (title, content, category, tags, source_video_id, importance)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)
    
    conn.commit()
    
    print("同步知识条目到FTS表...")
    cursor.execute("SELECT id, title, content, tags FROM knowledge")
    knowledge_items = cursor.fetchall()
    
    for item in knowledge_items:
        knowledge_id, title, content, tags = item
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_fts (rowid, title, content, tags)
            VALUES (?, ?, ?, ?)
        """, (knowledge_id, title, content, tags))
    
    conn.commit()
    
    print("\n=== 数据统计 ===")
    cursor.execute("SELECT COUNT(*) FROM videos")
    print(f"视频数量: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM knowledge")
    print(f"知识条目数量: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_fts")
    print(f"FTS索引数量: {cursor.fetchone()[0]}")
    
    print("\n=== 示例知识条目 ===")
    cursor.execute("SELECT id, title, category FROM knowledge LIMIT 3")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} - {row[2]}")
    
    conn.close()
    print("\n示例数据添加完成！现在可以测试搜索功能了。")

if __name__ == '__main__':
    add_sample_data()
