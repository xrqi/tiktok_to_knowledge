"""命令行版本的短视频知识提炼工具"""
import asyncio
import argparse
from src.core.video_acquisition import VideoAcquisition
from src.core.video_processing import VideoProcessor
from src.core.ai_analysis import AIAnalyzer, KnowledgeRefiner
from src.core.knowledge_manager import KnowledgeManager
from src.core.database_init import DatabaseManager
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

async def process_video_url(url: str):
    """处理视频URL"""
    # 初始化各模块
    va = VideoAcquisition()
    vp = VideoProcessor()
    aa = AIAnalyzer()
    km = KnowledgeManager()
    db = DatabaseManager()
    
    # 初始化数据库
    db.init_database()
    
    print(f"正在获取视频信息: {url}")
    video_info = await va.get_video_info(url, use_cookies=True)
    
    if not video_info:
        print("获取视频信息失败")
        return
    
    print(f"视频标题: {video_info['title']}")
    print(f"视频作者: {video_info['author']}")
    
    # 检查视频是否已存在
    existing_video = db.get_video_by_platform_id(video_info['platform'], video_info['video_id'])
    
    if existing_video:
        # 视频已存在，检查文件是否存在
        video_id = existing_video['id']
        video_filename = f"{existing_video['title']}.mp4"
        video_path = f"{va.config.download_dir}/{video_filename}"
        
        # 检查转录文本是否存在
        existing_transcript = db.get_transcript_by_video_id(video_id)
        
        if existing_transcript:
            # 转录文本已存在，直接使用
            text = existing_transcript['content']
            print("使用已存在的转录文本...")
        elif Path(video_path).exists():
            # 视频文件存在但转录文本不存在，提取音频
            print("使用已下载的视频，正在提取音频...")
            text = vp.process_video(video_path)
            if not text:
                print("视频处理失败")
                return
            
            # 保存转录文本
            db.insert_transcript(video_id, text)
        else:
            # 视频文件不存在，重新下载
            print("视频文件不存在，正在重新下载...")
            download_path = await va.download_video_by_info(video_info, va.config.download_dir, use_cookies=True)
            
            if not download_path:
                print("视频下载失败")
                return
            
            # 更新数据库状态
            db.update_video_status(video_id, 'downloaded')
            
            # 处理视频（提取音频并转换为文本）
            text = vp.process_video(download_path)
            if not text:
                print("视频处理失败")
                return
            
            # 保存转录文本
            db.insert_transcript(video_id, text)
    else:
        # 视频不存在，插入新记录
        video_id = db.insert_video(
            platform=video_info['platform'],
            video_id=video_info['video_id'],
            title=video_info['title'],
            author=video_info['author'],
            url=video_info['url'],
            duration=video_info.get('duration'),
            status='downloading'
        )
        
        print("正在下载视频...")
        download_path = await va.download_video_by_info(video_info, va.config.download_dir, use_cookies=True)
        
        if not download_path:
            print("视频下载失败")
            return
        
        # 更新数据库状态
        db.update_video_status(video_id, 'downloaded')
        
        # 处理视频（提取音频并转换为文本）
        text = vp.process_video(download_path)
        if not text:
            print("视频处理失败")
            return
        
        # 保存转录文本
        db.insert_transcript(video_id, text)
    
    # AI 分析
    print("正在分析内容...")
    knowledge_points = aa.extract_knowledge_points(text)
    
    print(f"AI 分析完成，提取到 {len(knowledge_points)} 个知识点")
    
    # 精炼知识点
    refined_knowledge = KnowledgeRefiner.refine_knowledge(knowledge_points)
    
    print(f"知识点精炼完成，精炼后数量: {len(refined_knowledge)}")
    
    # 保存知识点到数据库（使用批量插入）
    knowledge_list = []
    for kp in refined_knowledge:
        knowledge_list.append({
            'title': kp['title'],
            'content': kp['content'],
            'category': kp['category'],
            'tags': kp['tags'],
            'source_video_id': video_id,
            'importance': kp['importance']
        })
    
    km.add_knowledge_batch(knowledge_list)
    print(f"知识点已保存到数据库，数量: {len(knowledge_list)}")
    
    # 更新视频状态
    db.update_video_status(video_id, 'processed')
    
    print("处理完成!")
    
    # 显示结果
    print("\n提取的知识点：")
    print("=" * 80)
    for i, kp in enumerate(refined_knowledge, 1):
        print(f"\n知识点 {i}:")
        print(f"标题: {kp['title']}")
        print(f"内容: {kp['content'][:100]}...")
        print(f"分类: {kp['category']}")
        print(f"标签: {', '.join(kp['tags'])}")
        print(f"重要性: {kp['importance']}")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description='短视频知识提炼工具 - 命令行版本')
    parser.add_argument('url', type=str, nargs='?', help='视频URL')
    parser.add_argument('--list', action='store_true', help='列出所有知识点')
    parser.add_argument('--search', type=str, help='搜索知识点')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    if args.list:
        # 列出所有知识点
        km = KnowledgeManager()
        db = DatabaseManager()
        db.init_database()
        
        knowledge_list = km.get_all_knowledge()
        
        print(f"数据库中共有 {len(knowledge_list)} 条知识点")
        print("\n最近的知识点：")
        print("=" * 80)
        for i, kp in enumerate(knowledge_list[:20], 1):
            print(f"\n知识点 {i}:")
            print(f"ID: {kp['id']}")
            print(f"标题: {kp['title']}")
            print(f"分类: {kp['category']}")
            print(f"重要性: {kp['importance']}")
            print(f"创建时间: {kp['created_at']}")
            print("-" * 80)
    elif args.search:
        # 搜索知识点
        km = KnowledgeManager()
        db = DatabaseManager()
        db.init_database()
        
        results = km.search_knowledge(args.search)
        
        print(f"搜索 '{args.search}' 找到 {len(results)} 条知识点")
        print("\n搜索结果：")
        print("=" * 80)
        for i, kp in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"标题: {kp['title']}")
            print(f"内容: {kp['content'][:100]}...")
            print(f"分类: {kp['category']}")
            print("-" * 80)
    elif args.stats:
        # 显示统计信息
        km = KnowledgeManager()
        db = DatabaseManager()
        db.init_database()
        
        stats = km.get_knowledge_statistics()
        
        print("知识库统计信息")
        print("=" * 80)
        print(f"总视频数: {stats['total_videos']}")
        print(f"已处理视频: {stats['processed_videos']}")
        print(f"知识条目总数: {stats['total_knowledge']}")
        print(f"待复习知识: {stats['pending_reviews']}")
        print("\n分类统计：")
        for category, count in stats['top_categories']:
            print(f"  {category}: {count}")
        print("\n重要性分布：")
        for item in stats['importance_distribution']:
            print(f"  重要性 {item['importance']}: {item['count']} 条")
    elif args.url:
        # 处理视频URL
        asyncio.run(process_video_url(args.url))
    else:
        print("请指定操作：")
        print("  python cli.py <视频URL>              # 处理视频")
        print("  python cli.py --list                  # 列出所有知识点")
        print("  python cli.py --search <关键词>       # 搜索知识点")
        print("  python cli.py --stats                 # 显示统计信息")

if __name__ == "__main__":
    main()
