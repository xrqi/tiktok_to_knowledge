from flask import Flask, render_template, request, jsonify
from src.core.knowledge_manager import KnowledgeManager
from src.core.database_init import DatabaseManager
import asyncio
import threading
import uuid
from datetime import datetime
from src.core.video_acquisition import VideoAcquisition
from src.core.video_processing import VideoProcessor
from src.core.ai_analysis import AIAnalyzer, KnowledgeRefiner
from src.core.knowledge_manager import KnowledgeManager as KM
from pathlib import Path

app = Flask(__name__)

km = KnowledgeManager()
db = DatabaseManager()
db.init_database()

# 任务管理系统
tasks = {}
task_lock = threading.Lock()

class TaskProgress:
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = 'pending'
        self.progress = 0
        self.message = '等待开始...'
        self.result = None
        self.error = None
        self.created_at = datetime.now()
    
    def update(self, progress, message):
        self.progress = progress
        self.message = message
    
    def set_status(self, status, message=None):
        self.status = status
        if message:
            self.message = message
    
    def set_result(self, result):
        self.result = result
        self.status = 'completed'
        self.progress = 100
        self.message = '完成！'
    
    def set_error(self, error):
        self.error = str(error)
        self.status = 'failed'
        self.message = f'失败: {error}'
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat()
        }

async def process_video_url(url: str, progress_callback=None):
    """处理视频URL"""
    def update_progress(progress, message):
        if progress_callback:
            progress_callback(progress, message)
    
    # 初始化各模块
    va = VideoAcquisition()
    vp = VideoProcessor()
    aa = AIAnalyzer()
    km = KM()
    
    update_progress(5, '正在获取视频信息...')
    print(f"正在获取视频信息: {url}")
    video_info = await va.get_video_info(url, use_cookies=True)
    
    if not video_info:
        raise Exception("获取视频信息失败")
    
    # 验证video_id是否存在
    if not video_info.get('video_id'):
        raise Exception("无法获取视频ID，请检查视频URL是否正确")
    
    print(f"视频标题: {video_info['title']}")
    print(f"视频作者: {video_info['author']}")
    
    update_progress(10, '检查视频是否已存在...')
    
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
            update_progress(40, '使用已存在的转录文本...')
        elif Path(video_path).exists():
            # 视频文件存在但转录文本不存在，提取音频
            print("使用已下载的视频，正在提取音频...")
            update_progress(30, '正在提取音频...')
            text = vp.process_video(video_path)
            if not text:
                raise Exception("视频处理失败")
            
            # 保存转录文本
            db.insert_transcript(video_id, text)
            update_progress(40, '音频提取完成...')
        else:
            # 视频文件不存在，重新下载
            print("视频文件不存在，正在重新下载...")
            update_progress(20, '正在下载视频...')
            download_path = await va.download_video_by_info(video_info, va.config.download_dir, use_cookies=True)
            
            if not download_path:
                raise Exception("视频下载失败")
            
            # 更新数据库状态
            db.update_video_status(video_id, 'downloaded')
            
            # 处理视频（提取音频并转换为文本）
            update_progress(30, '正在提取音频...')
            text = vp.process_video(download_path)
            if not text:
                raise Exception("视频处理失败")
            
            # 保存转录文本
            db.insert_transcript(video_id, text)
            update_progress(40, '音频提取完成...')
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
        update_progress(20, '正在下载视频...')
        download_path = await va.download_video_by_info(video_info, va.config.download_dir, use_cookies=True)
        
        if not download_path:
            raise Exception("视频下载失败")
        
        # 更新数据库状态
        db.update_video_status(video_id, 'downloaded')
        
        # 处理视频（提取音频并转换为文本）
        update_progress(30, '正在提取音频...')
        text = vp.process_video(download_path)
        if not text:
            raise Exception("视频处理失败")
        
        # 保存转录文本
        db.insert_transcript(video_id, text)
        update_progress(40, '音频提取完成...')
    
    # AI 分析
    print("正在分析内容...")
    update_progress(50, '正在使用AI分析内容...')
    knowledge_points = aa.extract_knowledge_points(text)
    
    print(f"AI 分析完成，提取到 {len(knowledge_points)} 个知识点")
    update_progress(70, f'AI分析完成，提取到 {len(knowledge_points)} 个知识点...')
    
    # 精炼知识点
    update_progress(80, '正在精炼知识点...')
    refined_knowledge = KnowledgeRefiner.refine_knowledge(knowledge_points)
    
    print(f"知识点精炼完成，精炼后数量: {len(refined_knowledge)}")
    
    # 保存知识点到数据库（使用批量插入）
    update_progress(90, '正在保存到数据库...')
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
    update_progress(100, '处理完成！')
    
    return len(knowledge_list)

def run_task_async(task_id, url):
    """在后台线程中运行任务"""
    print(f"[DEBUG] 任务 {task_id} 开始处理，URL: {url}")
    task = tasks[task_id]
    
    def progress_callback(progress, message):
        task.update(progress, message)
    
    try:
        task.set_status('running', '任务开始...')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(process_video_url(url, progress_callback))
            task.set_result(result)
        finally:
            loop.close()
    except Exception as e:
        task.set_error(e)
        print(f"任务 {task_id} 失败: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/graph')
def graph():
    """知识图谱页面"""
    return render_template('graph.html')

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    if search:
        knowledge_list = km.search_knowledge(search)
    else:
        knowledge_list = km.get_all_knowledge()
    
    total = len(knowledge_list)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_list = knowledge_list[start:end]
    
    return jsonify({
        'knowledge': paginated_list,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/knowledge/<int:knowledge_id>', methods=['GET'])
def get_knowledge_detail(knowledge_id):
    knowledge = km.get_knowledge_by_id(knowledge_id)
    if knowledge:
        return jsonify(knowledge)
    return jsonify({'error': 'Knowledge not found'}), 404

@app.route('/api/knowledge/<int:knowledge_id>', methods=['PUT'])
def update_knowledge(knowledge_id):
    data = request.get_json()
    success = km.update_knowledge(
        knowledge_id=knowledge_id,
        title=data.get('title'),
        content=data.get('content'),
        category=data.get('category'),
        tags=data.get('tags', []),
        importance=data.get('importance')
    )
    
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to update knowledge'}), 400

@app.route('/api/knowledge/<int:knowledge_id>', methods=['DELETE'])
def delete_knowledge(knowledge_id):
    success = km.delete_knowledge(knowledge_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': 'Failed to delete knowledge'}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats = km.get_knowledge_statistics()
    return jsonify(stats)

@app.route('/api/analyze', methods=['POST'])
def analyze_video():
    """分析视频并导入知识库（异步）"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': '请提供视频URL'}), 400
        
        # 从输入中提取URL（如果用户输入了额外的文本）
        import re
        url_pattern = r'https?://(?:v\.douyin\.com|www\.douyin\.com|douyin\.com)/[^\s]+'
        match = re.search(url_pattern, url)
        if match:
            url = match.group(0)
        
        if not url or not url.startswith('http'):
            return jsonify({'success': False, 'error': '无效的URL格式'}), 400
        
        # 创建新任务
        task_id = str(uuid.uuid4())
        task = TaskProgress(task_id)
        
        with task_lock:
            tasks[task_id] = task
        
        # 在后台线程中运行任务
        thread = threading.Thread(target=run_task_async, args=(task_id, url))
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'task_id': task_id})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    with task_lock:
        task = tasks.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(task.to_dict())

@app.route('/api/knowledge-graph', methods=['GET'])
def get_knowledge_graph():
    """获取知识图谱数据"""
    try:
        knowledge_list = km.get_all_knowledge(limit=1000)
        
        nodes = []
        edges = []
        node_id_map = {}
        category_nodes = {}
        tag_nodes = {}
        video_nodes = {}
        
        for idx, kp in enumerate(knowledge_list):
            kp_id = kp['id']
            kp_title = kp['title'] or '无标题'
            kp_category = kp['category'] or '未分类'
            kp_tags = ensure_array(kp['tags'])
            kp_video_id = kp.get('source_video_id')
            kp_video_title = kp.get('video_title') or '未知视频'
            
            node_id_map[kp_id] = f'kp_{kp_id}'
            
            nodes.append({
                'id': f'kp_{kp_id}',
                'name': kp_title,
                'category': '知识',
                'symbolSize': 30,
                'itemStyle': {'color': '#6366f1'},
                'data': {
                    'id': kp_id,
                    'content': kp['content'] or '',
                    'category': kp_category,
                    'tags': kp_tags,
                    'importance': kp['importance'],
                    'created_at': kp['created_at']
                }
            })
            
            if kp_category not in category_nodes:
                cat_id = f'cat_{kp_category}'
                category_nodes[kp_category] = cat_id
                nodes.append({
                    'id': cat_id,
                    'name': kp_category,
                    'category': '分类',
                    'symbolSize': 40,
                    'itemStyle': {'color': '#8b5cf6'},
                    'data': {'type': 'category'}
                })
            
            edges.append({
                'source': f'kp_{kp_id}',
                'target': category_nodes[kp_category],
                'name': '属于',
                'lineStyle': {'color': '#8b5cf6', 'width': 2}
            })
            
            for tag in kp_tags:
                if tag not in tag_nodes:
                    tag_id = f'tag_{tag}'
                    tag_nodes[tag] = tag_id
                    nodes.append({
                        'id': tag_id,
                        'name': tag,
                        'category': '标签',
                        'symbolSize': 25,
                        'itemStyle': {'color': '#10b981'},
                        'data': {'type': 'tag'}
                    })
                
                edges.append({
                    'source': f'kp_{kp_id}',
                    'target': tag_nodes[tag],
                    'name': '标签',
                    'lineStyle': {'color': '#10b981', 'width': 1}
                })
            
            if kp_video_id:
                if kp_video_id not in video_nodes:
                    vid_id = f'vid_{kp_video_id}'
                    video_nodes[kp_video_id] = vid_id
                    nodes.append({
                        'id': vid_id,
                        'name': kp_video_title,
                        'category': '视频',
                        'symbolSize': 35,
                        'itemStyle': {'color': '#f59e0b'},
                        'data': {'type': 'video', 'video_id': kp_video_id}
                    })
                
                edges.append({
                    'source': f'kp_{kp_id}',
                    'target': video_nodes[kp_video_id],
                    'name': '来源',
                    'lineStyle': {'color': '#f59e0b', 'width': 2}
                })
        
        for i, kp1 in enumerate(knowledge_list):
            for j, kp2 in enumerate(knowledge_list):
                if i >= j:
                    continue
                
                tags1 = set(ensure_array(kp1['tags']))
                tags2 = set(ensure_array(kp2['tags']))
                common_tags = tags1 & tags2
                
                if common_tags:
                    for tag in common_tags:
                        edges.append({
                            'source': f'kp_{kp1["id"]}',
                            'target': f'kp_{kp2["id"]}',
                            'name': f'共同标签: {tag}',
                            'lineStyle': {'color': '#10b981', 'width': 1, 'type': 'dashed'}
                        })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges,
            'categories': ['知识', '分类', '标签', '视频']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def ensure_array(tags):
    """确保tags是列表格式"""
    if isinstance(tags, list):
        return tags
    elif isinstance(tags, str):
        try:
            import json
            return json.loads(tags)
        except:
            return [tag.strip() for tag in tags.split(',') if tag.strip()]
    else:
        return []

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='知识管理Web应用')
    parser.add_argument('--host', default='0.0.0.0', help='主机地址')
    parser.add_argument('--port', type=int, default=5000, help='端口号')
    parser.add_argument('--debug', action='store_true', help='调试模式')
    args = parser.parse_args()
    
    app.run(debug=args.debug, host=args.host, port=args.port, threaded=True)
