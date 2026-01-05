import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "./data/knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        conn.execute("PRAGMA busy_timeout=5000")  # 设置超时时间为5秒
        # 不使用 WAL 模式，避免数据库损坏问题
        conn.execute("PRAGMA journal_mode=DELETE")  # 使用 DELETE 模式
        conn.execute("PRAGMA synchronous=NORMAL")  # 设置同步模式
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 创建视频信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                url TEXT NOT NULL,
                duration INTEGER,
                download_path TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                metadata TEXT  -- JSON格式的额外元数据
            )
        """)
        
        # 创建转录文本表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                language TEXT DEFAULT 'zh',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE
            )
        """)
        
        # 创建知识条目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,  -- JSON数组格式的标签
                source_video_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                importance INTEGER DEFAULT 1,  -- 重要性等级 1-5
                next_review_date TIMESTAMP,
                review_count INTEGER DEFAULT 0,
                FOREIGN KEY (source_video_id) REFERENCES videos (id) ON DELETE SET NULL
            )
        """)
        
        # 创建知识条目全文搜索虚拟表（使用trigram分词器支持中文搜索）
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts 
            USING fts5(title, content, tags, content_rowid='id', tokenize='trigram')
        """)
        
        # 创建复习记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER NOT NULL,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recall_success BOOLEAN NOT NULL,
                ease_factor REAL DEFAULT 2.5,
                interval_days INTEGER DEFAULT 1,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge (id) ON DELETE CASCADE
            )
        """)
        
        # 创建配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT
            )
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_platform ON videos(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_importance ON knowledge(importance)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_next_review ON knowledge(next_review_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_video_id ON transcripts(video_id)")
        
        conn.commit()
        conn.close()
        
        self.logger.info("数据库初始化完成")
    
    def insert_video(self, platform: str, video_id: str, title: str, author: str, url: str, 
                    duration: Optional[int] = None, download_path: Optional[str] = None, 
                    status: str = 'pending', metadata: Optional[Dict[str, Any]] = None) -> int:
        """插入视频信息，如果已存在则更新"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        metadata_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
        
        try:
            # 检查视频是否已存在
            cursor.execute("SELECT id FROM videos WHERE platform = ? AND video_id = ?", (platform, video_id))
            existing_video = cursor.fetchone()
            
            if existing_video:
                # 如果视频已存在，更新现有记录
                cursor.execute("""
                    UPDATE videos 
                    SET title=?, author=?, url=?, duration=?, download_path=?, status=?, metadata=?, updated_at=CURRENT_TIMESTAMP
                    WHERE platform=? AND video_id=?
                """, (title, author, url, duration, download_path, status, metadata_json, platform, video_id))
                
                video_db_id = existing_video['id']
            else:
                # 如果视频不存在，插入新记录
                cursor.execute("""
                    INSERT INTO videos (platform, video_id, title, author, url, duration, download_path, status, metadata, download_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (platform, video_id, title, author, url, duration, download_path, status, metadata_json))
                
                video_db_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            return video_db_id
        except Exception as e:
            conn.close()
            raise e
    
    def get_video_by_id(self, video_id: int) -> Optional[sqlite3.Row]:
        """根据ID获取视频信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def get_video_by_platform_id(self, platform: str, platform_video_id: str) -> Optional[sqlite3.Row]:
        """根据平台和视频ID获取视频信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE platform = ? AND video_id = ?", (platform, platform_video_id))
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def update_video_status(self, video_id: int, status: str):
        """更新视频状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE videos SET status = ? WHERE id = ?", (status, video_id))
        conn.commit()
        conn.close()
    
    def insert_transcript(self, video_id: int, content: str, language: str = 'zh'):
        """插入转录文本"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transcripts (video_id, content, language)
            VALUES (?, ?, ?)
        """, (video_id, content, language))
        
        transcript_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transcript_id
    
    def get_transcript_by_video_id(self, video_id: int) -> Optional[sqlite3.Row]:
        """根据视频ID获取转录文本"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM transcripts WHERE video_id = ?", (video_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result
    
    def insert_knowledge(self, title: str, content: str, category: Optional[str] = None,
                        tags: Optional[List[str]] = None, source_video_id: Optional[int] = None,
                        importance: int = 1) -> int:
        """插入知识条目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            tags_json = json.dumps(tags, ensure_ascii=False) if tags else '[]'
            
            cursor.execute("""
                INSERT INTO knowledge (title, content, category, tags, source_video_id, importance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, content, category, tags_json, source_video_id, importance))
            
            knowledge_id = cursor.lastrowid
            
            # 暂时禁用 FTS 同步，避免数据库损坏问题
            # 同步到全文搜索表（在同一个连接中）
            # try:
            #     cursor.execute("DELETE FROM knowledge_fts WHERE rowid = ?", (knowledge_id,))
            #     cursor.execute("""
            #         INSERT INTO knowledge_fts (rowid, title, content, tags)
            #         VALUES (?, ?, ?, ?)
            #     """, (knowledge_id, title, content, tags_json))
            # except Exception as e:
            #     self.logger.warning(f"同步到全文搜索表失败: {e}")
            
            conn.commit()
            return knowledge_id
        except Exception as e:
            conn.rollback()
            self.logger.error(f"插入知识条目失败: {e}")
            raise
        finally:
            conn.close()
    
    def insert_knowledge_batch(self, knowledge_list: List[Dict[str, Any]]) -> List[int]:
        """批量插入知识条目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            knowledge_ids = []
            
            for kp in knowledge_list:
                tags_json = json.dumps(kp.get('tags', []), ensure_ascii=False)
                
                cursor.execute("""
                    INSERT INTO knowledge (title, content, category, tags, source_video_id, importance)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    kp.get('title', ''),
                    kp.get('content', ''),
                    kp.get('category'),
                    tags_json,
                    kp.get('source_video_id'),
                    kp.get('importance', 1)
                ))
                
                knowledge_id = cursor.lastrowid
                knowledge_ids.append(knowledge_id)
                
                # 同步到全文搜索表
                try:
                    cursor.execute("DELETE FROM knowledge_fts WHERE rowid = ?", (knowledge_id,))
                    cursor.execute("""
                        INSERT INTO knowledge_fts (rowid, title, content, tags)
                        VALUES (?, ?, ?, ?)
                    """, (knowledge_id, kp.get('title', ''), kp.get('content', ''), tags_json))
                except Exception as e:
                    self.logger.warning(f"同步到全文搜索表失败: {e}")
            
            conn.commit()
            return knowledge_ids
        except Exception as e:
            conn.rollback()
            self.logger.error(f"批量插入知识条目失败: {e}")
            raise
        finally:
            conn.close()
    
    def _sync_knowledge_to_fts(self, knowledge_id: int):
        """同步知识条目到全文搜索表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先删除旧的索引
        cursor.execute("DELETE FROM knowledge_fts WHERE rowid = ?", (knowledge_id,))
        
        # 获取知识条目内容
        cursor.execute("""
            SELECT title, content, tags FROM knowledge WHERE id = ?
        """, (knowledge_id,))
        row = cursor.fetchone()
        
        if row:
            # 插入新的索引
            cursor.execute("""
                INSERT INTO knowledge_fts (rowid, title, content, tags)
                VALUES (?, ?, ?, ?)
            """, (knowledge_id, row['title'], row['content'], row['tags']))
        
        conn.commit()
        conn.close()
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[sqlite3.Row]:
        """全文搜索知识条目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先尝试FTS全文搜索
        cursor.execute("""
            SELECT k.*, t.title as video_title, t.url as video_url
            FROM knowledge k
            LEFT JOIN videos t ON k.source_video_id = t.id
            WHERE k.id IN (
                SELECT rowid FROM knowledge_fts
                WHERE knowledge_fts MATCH ?
            )
            ORDER BY k.importance DESC
            LIMIT ?
        """, (query, limit))
        
        results = cursor.fetchall()
        
        # 如果FTS搜索没有结果，使用LIKE搜索作为fallback
        if not results:
            like_query = f"%{query}%"
            cursor.execute("""
                SELECT k.*, t.title as video_title, t.url as video_url
                FROM knowledge k
                LEFT JOIN videos t ON k.source_video_id = t.id
                WHERE k.title LIKE ? OR k.content LIKE ? OR k.tags LIKE ?
                ORDER BY k.importance DESC
                LIMIT ?
            """, (like_query, like_query, like_query, limit))
            results = cursor.fetchall()
        
        conn.close()
        
        return results
    
    def get_knowledge_by_category(self, category: str, limit: int = 10) -> List[sqlite3.Row]:
        """根据分类获取知识条目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT k.*, t.title as video_title
            FROM knowledge k
            LEFT JOIN videos t ON k.source_video_id = t.id
            WHERE k.category = ?
            ORDER BY k.importance DESC, k.created_at DESC
            LIMIT ?
        """, (category, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_pending_reviews(self) -> List[sqlite3.Row]:
        """获取待复习的知识条目"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT k.*, t.title as video_title
            FROM knowledge k
            LEFT JOIN videos t ON k.source_video_id = t.id
            WHERE k.next_review_date <= datetime('now')
            ORDER BY k.next_review_date ASC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def update_review_record(self, knowledge_id: int, recall_success: bool):
        """更新复习记录（使用间隔重复算法）"""
        import math
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 获取当前知识条目的复习信息
        cursor.execute("""
            SELECT importance, next_review_date, review_count, ease_factor
            FROM knowledge
            WHERE id = ?
        """, (knowledge_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return
        
        # 获取上一次复习记录
        cursor.execute("""
            SELECT recall_success, ease_factor, interval_days
            FROM review_records
            WHERE knowledge_id = ?
            ORDER BY review_date DESC
            LIMIT 1
        """)
        last_review = cursor.fetchone()
        
        # 计算新的间隔和难度因子
        if last_review:
            ease_factor = last_review['ease_factor']
            interval_days = last_review['interval_days']
        else:
            ease_factor = 2.5
            interval_days = 1
        
        # 根据间隔重复算法调整
        if recall_success:
            if last_review is None:  # 首次复习
                new_interval = 1  # 1天后复习
            elif interval_days == 1:
                new_interval = 3  # 3天后复习
            else:
                # 使用SM-2算法公式
                new_interval = max(1, round(interval_days * ease_factor))
        else:
            # 如果回忆失败，重置间隔为1天
            new_interval = 1
        
        # 调整难度因子
        if recall_success:
            ease_factor = max(1.3, ease_factor + 0.1 - (5 - 4) * 0.08)
        else:
            ease_factor = max(1.3, ease_factor - 0.2)
        
        # 更新知识条目的下次复习日期
        cursor.execute("""
            UPDATE knowledge
            SET next_review_date = datetime('now', '+{} days'),
                review_count = review_count + 1,
                ease_factor = ?
            WHERE id = ?
        """, (new_interval, ease_factor, knowledge_id))
        
        # 记录本次复习
        cursor.execute("""
            INSERT INTO review_records (knowledge_id, recall_success, ease_factor, interval_days)
            VALUES (?, ?, ?, ?)
        """, (knowledge_id, recall_success, ease_factor, new_interval))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 总视频数
        cursor.execute("SELECT COUNT(*) as count FROM videos")
        total_videos = cursor.fetchone()['count']
        
        # 已处理视频数
        cursor.execute("SELECT COUNT(*) as count FROM videos WHERE status = 'processed'")
        processed_videos = cursor.fetchone()['count']
        
        # 知识条目总数
        cursor.execute("SELECT COUNT(*) as count FROM knowledge")
        total_knowledge = cursor.fetchone()['count']
        
        # 待复习知识条目数
        cursor.execute("""
            SELECT COUNT(*) as count FROM knowledge
            WHERE next_review_date <= datetime('now')
        """)
        pending_reviews = cursor.fetchone()['count']
        
        # 知识分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM knowledge
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        category_stats = {row['category']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total_videos': total_videos,
            'processed_videos': processed_videos,
            'total_knowledge': total_knowledge,
            'pending_reviews': pending_reviews,
            'category_stats': category_stats
        }

if __name__ == "__main__":
    # 初始化数据库
    db_manager = DatabaseManager()
    db_manager.init_database()
    print("数据库初始化完成")