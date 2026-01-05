from src.core.database_init import DatabaseManager
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime, timedelta
import json

class KnowledgeManager:
    def __init__(self, db_path: str = "./data/knowledge.db"):
        self.db_manager = DatabaseManager(db_path)
        self.logger = logging.getLogger(__name__)
    
    def save_or_update_video_info(self, video_data: Dict[str, Any]) -> int:
        """保存或更新视频信息"""
        try:
            video_db_id = self.db_manager.insert_video(
                platform=video_data['platform'],
                video_id=video_data['video_id'],
                title=video_data['title'],
                author=video_data['author'],
                url=video_data['url'],
                duration=video_data.get('duration'),
                download_path=video_data.get('download_path'),
                status=video_data.get('status', 'pending'),
                metadata=video_data.get('metadata')
            )
            
            self.logger.info(f"视频信息已保存/更新，数据库ID: {video_db_id}")
            return video_db_id
        except Exception as e:
            self.logger.error(f"保存视频信息失败: {e}")
            raise e
    
    def get_video_by_platform_and_id(self, platform: str, video_id: str) -> Optional[Dict[str, Any]]:
        """根据平台和视频ID获取视频信息"""
        video = self.db_manager.get_video_by_platform_id(platform, video_id)
        if video:
            return dict(video)
        return None
    
    def add_knowledge(self, title: str, content: str, category: Optional[str] = None,
                     tags: Optional[List[str]] = None, source_video_id: Optional[int] = None,
                     importance: int = 3) -> int:
        """添加知识条目"""
        try:
            knowledge_id = self.db_manager.insert_knowledge(
                title=title,
                content=content,
                category=category,
                tags=tags,
                source_video_id=source_video_id,
                importance=importance
            )
            
            self.logger.info(f"知识条目已添加，ID: {knowledge_id}")
            return knowledge_id
        except Exception as e:
            self.logger.error(f"添加知识条目失败: {e}")
            return 0
    
    def add_knowledge_batch(self, knowledge_list: List[Dict[str, Any]]) -> List[int]:
        """批量添加知识条目"""
        try:
            knowledge_ids = self.db_manager.insert_knowledge_batch(knowledge_list)
            self.logger.info(f"批量添加知识条目成功，数量: {len(knowledge_ids)}")
            return knowledge_ids
        except Exception as e:
            self.logger.error(f"批量添加知识条目失败: {e}")
            return []
    
    def get_knowledge_by_id(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取知识条目"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT k.*, v.title as video_title, v.author as video_author, v.url as video_url
            FROM knowledge k
            LEFT JOIN videos v ON k.source_video_id = v.id
            WHERE k.id = ?
        """, (knowledge_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索知识条目"""
        results = self.db_manager.search_knowledge(query, limit)
        return [dict(row) for row in results]
    
    def get_knowledge_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """根据分类获取知识条目"""
        results = self.db_manager.get_knowledge_by_category(category, limit)
        return [dict(row) for row in results]
    
    def get_all_categories(self) -> List[str]:
        """获取所有知识分类"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT category 
            FROM knowledge 
            WHERE category IS NOT NULL 
            ORDER BY category
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [row['category'] for row in results if row['category']]
    
    def get_all_knowledge(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取所有知识条目"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT k.id, k.title, k.content, k.category, k.tags, k.importance, k.created_at, v.title as video_title, v.url as video_url
            FROM knowledge k
            LEFT JOIN videos v ON k.source_video_id = v.id
            ORDER BY k.created_at DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def update_knowledge(self, knowledge_id: int, title: Optional[str] = None,
                        content: Optional[str] = None, category: Optional[str] = None,
                        tags: Optional[List[str]] = None, importance: Optional[int] = None) -> bool:
        """更新知识条目"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = ?")
            params.append(title)
        if content is not None:
            update_fields.append("content = ?")
            params.append(content)
        if category is not None:
            update_fields.append("category = ?")
            params.append(category)
        if tags is not None:
            tags_json = json.dumps(tags, ensure_ascii=False)
            update_fields.append("tags = ?")
            params.append(tags_json)
        if importance is not None:
            update_fields.append("importance = ?")
            params.append(importance)
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(knowledge_id)
        
        if update_fields:
            sql = f"UPDATE knowledge SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
            conn.close()
            
            self.logger.info(f"知识条目已更新，ID: {knowledge_id}")
            # 同步到全文搜索
            self.db_manager._sync_knowledge_to_fts(knowledge_id)
            return True
        
        conn.close()
        return False
    
    def delete_knowledge(self, knowledge_id: int) -> bool:
        """删除知识条目"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected_rows > 0:
            self.logger.info(f"知识条目已删除，ID: {knowledge_id}")
            return True
        return False
    
    def get_pending_reviews(self) -> List[Dict[str, Any]]:
        """获取待复习的知识条目"""
        results = self.db_manager.get_pending_reviews()
        return [dict(row) for row in results]
    
    def mark_review(self, knowledge_id: int, recall_success: bool) -> bool:
        """标记知识条目复习状态"""
        try:
            self.db_manager.update_review_record(knowledge_id, recall_success)
            self.logger.info(f"知识条目复习记录已更新，ID: {knowledge_id}, 回忆成功: {recall_success}")
            return True
        except Exception as e:
            self.logger.error(f"更新复习记录失败: {e}")
            return False
    
    def get_review_statistics(self) -> Dict[str, Any]:
        """获取复习统计信息"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 获取总的复习记录
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                AVG(CASE WHEN recall_success THEN 1.0 ELSE 0.0 END) as success_rate,
                COUNT(CASE WHEN recall_success THEN 1 END) as successful_reviews,
                COUNT(CASE WHEN NOT recall_success THEN 1 END) as failed_reviews
            FROM review_records
            WHERE review_date >= datetime('now', '-30 days')
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'total_reviews': result['total_reviews'] or 0,
            'success_rate': result['success_rate'] or 0.0,
            'successful_reviews': result['successful_reviews'] or 0,
            'failed_reviews': result['failed_reviews'] or 0
        }
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = self.db_manager.get_statistics()
        
        # 添加额外的统计信息
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # 获取最活跃的分类
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM knowledge
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        """)
        
        top_categories = [{"category": row['category'], "count": row['count']} 
                         for row in cursor.fetchall()]
        
        # 获取重要性分布
        cursor.execute("""
            SELECT importance, COUNT(*) as count
            FROM knowledge
            GROUP BY importance
            ORDER BY importance DESC
        """)
        
        importance_distribution = [{"importance": row['importance'], "count": row['count']} 
                                 for row in cursor.fetchall()]
        
        conn.close()
        
        stats['top_categories'] = top_categories
        stats['importance_distribution'] = importance_distribution
        
        return stats
    
    def batch_add_knowledge(self, knowledge_list: List[Dict[str, Any]]) -> List[int]:
        """批量添加知识条目"""
        added_ids = []
        
        for knowledge in knowledge_list:
            knowledge_id = self.add_knowledge(
                title=knowledge.get('title', ''),
                content=knowledge.get('content', ''),
                category=knowledge.get('category'),
                tags=knowledge.get('tags'),
                source_video_id=knowledge.get('source_video_id'),
                importance=knowledge.get('importance', 3)
            )
            
            if knowledge_id:
                added_ids.append(knowledge_id)
        
        return added_ids
    
    def export_knowledge(self, category: Optional[str] = None, 
                        tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """导出知识条目"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT k.*, v.title as video_title, v.author as video_author
            FROM knowledge k
            LEFT JOIN videos v ON k.source_video_id = v.id
        """
        
        conditions = []
        params = []
        
        if category:
            conditions.append("k.category = ?")
            params.append(category)
        
        if tags:
            # 查找包含任意一个指定标签的知识条目
            for tag in tags:
                conditions.append("k.tags LIKE ?")
                params.append(f'%{tag}%')
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY k.importance DESC, k.created_at DESC"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def import_knowledge(self, knowledge_data: List[Dict[str, Any]]) -> int:
        """导入知识条目"""
        imported_count = 0
        
        for knowledge in knowledge_data:
            try:
                # 检查是否已存在相同标题的知识条目
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id FROM knowledge WHERE title = ? AND content = ?",
                    (knowledge.get('title', ''), knowledge.get('content', ''))
                )
                
                existing = cursor.fetchone()
                conn.close()
                
                if not existing:
                    # 如果不存在，则添加
                    knowledge_id = self.add_knowledge(
                        title=knowledge.get('title', ''),
                        content=knowledge.get('content', ''),
                        category=knowledge.get('category'),
                        tags=knowledge.get('tags'),
                        source_video_id=knowledge.get('source_video_id'),
                        importance=knowledge.get('importance', 3)
                    )
                    
                    if knowledge_id:
                        imported_count += 1
                else:
                    # 如果存在，可以选择更新
                    self.update_knowledge(
                        knowledge_id=existing['id'],
                        content=knowledge.get('content'),
                        category=knowledge.get('category'),
                        tags=knowledge.get('tags'),
                        importance=knowledge.get('importance', 3)
                    )
                    imported_count += 1
            except Exception as e:
                self.logger.error(f"导入知识条目失败: {e}")
        
        self.logger.info(f"成功导入 {imported_count} 个知识条目")
        return imported_count

class KnowledgeOrganizer:
    """知识组织器 - 提供高级知识管理功能"""
    
    def __init__(self, knowledge_manager: KnowledgeManager):
        self.km = knowledge_manager
    
    def create_knowledge_map(self, category: Optional[str] = None) -> Dict[str, Any]:
        """创建知识图谱（简化版）"""
        # 获取知识条目
        if category:
            knowledge_items = self.km.get_knowledge_by_category(category, limit=100)
        else:
            knowledge_items = self.km.export_knowledge()
        
        # 简单的基于标签的关联
        knowledge_map = {
            "nodes": [],
            "links": []
        }
        
        # 创建节点
        for item in knowledge_items:
            node = {
                "id": item['id'],
                "title": item['title'],
                "category": item['category'],
                "importance": item['importance'],
                "tags": json.loads(item['tags']) if item['tags'] else []
            }
            knowledge_map["nodes"].append(node)
        
        # 创建连接（基于共同标签）
        for i, item1 in enumerate(knowledge_items):
            tags1 = set(json.loads(item1['tags']) if item1['tags'] else [])
            
            for j, item2 in enumerate(knowledge_items[i+1:], i+1):
                tags2 = set(json.loads(item2['tags']) if item2['tags'] else [])
                
                common_tags = tags1.intersection(tags2)
                if common_tags:
                    link = {
                        "source": item1['id'],
                        "target": item2['id'],
                        "value": len(common_tags)
                    }
                    knowledge_map["links"].append(link)
        
        return knowledge_map
    
    def generate_study_plan(self, days: int = 7) -> List[Dict[str, Any]]:
        """生成学习计划"""
        # 获取待复习的知识条目
        pending_reviews = self.km.get_pending_reviews()
        
        # 按重要性排序
        pending_reviews.sort(key=lambda x: x['importance'], reverse=True)
        
        # 分配到不同天
        study_plan = []
        days_per_batch = max(1, len(pending_reviews) // days)
        
        for i, knowledge in enumerate(pending_reviews):
            day = (i // days_per_batch) % days
            if day >= len(study_plan):
                study_plan.append({"day": day + 1, "knowledge": []})
            
            study_plan[day]["knowledge"].append({
                "id": knowledge['id'],
                "title": knowledge['title'],
                "content": knowledge['content'][:100] + "..." if len(knowledge['content']) > 100 else knowledge['content']
            })
        
        return study_plan

# 使用示例
def main():
    km = KnowledgeManager()
    
    # 添加示例知识条目
    knowledge_id = km.add_knowledge(
        title="人工智能简介",
        content="人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        category="科技",
        tags=["AI", "机器学习", "计算机科学"],
        importance=4
    )
    
    print(f"添加的知识条目ID: {knowledge_id}")
    
    # 搜索知识
    results = km.search_knowledge("人工智能")
    print(f"搜索结果数量: {len(results)}")
    
    # 获取待复习的知识
    pending_reviews = km.get_pending_reviews()
    print(f"待复习知识数量: {len(pending_reviews)}")
    
    # 获取统计信息
    stats = km.get_knowledge_statistics()
    print(f"统计信息: {stats}")

if __name__ == "__main__":
    main()