import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from typing import List, Dict, Any, Optional
import webbrowser
from pathlib import Path
from datetime import datetime
import json
import os
import logging

from src.core.video_acquisition import VideoAcquisition
from src.core.video_processing import VideoProcessor
from src.core.ai_analysis import AIAnalyzer, KnowledgeRefiner
from src.core.knowledge_manager import KnowledgeManager
from src.core.database_init import DatabaseManager
from src.core.config import config_manager
from src.core.system_monitor import SystemMonitor, SystemMetrics

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("短视频知识提炼工具")
        self.root.geometry("1200x800")
        
        # 初始化 logger
        self.logger = logging.getLogger(__name__)
        
        # 初始化各模块
        self.video_acquisition = VideoAcquisition()
        self.video_processor = VideoProcessor()
        self.ai_analyzer = AIAnalyzer()
        self.knowledge_manager = KnowledgeManager()
        self.db_manager = DatabaseManager()
        self.system_monitor = SystemMonitor()
        self.system_monitor.callbacks.append(self.update_system_metrics)
        
        # 初始化变量
        self.current_video_info = None
        self.processing_thread = None
        self.is_processing = False
        self._last_network_metrics = {'bytes_recv': 0, 'bytes_sent': 0}
        self._last_metrics_timestamp = datetime.now()
        
        # 创建GUI组件
        self.create_widgets()
        
        # 启动系统监控
        self.system_monitor.start_monitoring()
        
        # 初始化数据库
        self.db_manager.init_database()
        
        # 加载初始统计数据
        self.load_statistics()
        
        # 加载知识点
        self.load_knowledge()
    
    def is_logged_in(self) -> bool:
        """检查是否已登录（通过检查cookie文件是否存在且包含关键登录cookies）"""
        cookie_file = "douyin_cookies.json"
        if not os.path.exists(cookie_file):
            return False
        
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                return False
            
            # 检查是否有过期的cookies
            import time
            current_time = time.time()
            valid_cookies = []
            
            for cookie in cookies:
                expires = cookie.get('expires', 0)
                if expires == -1:
                    valid_cookies.append(cookie)
                elif isinstance(expires, (int, float)) and expires > current_time:
                    valid_cookies.append(cookie)
                elif expires == 0 or expires is None:
                    valid_cookies.append(cookie)
            
            # 检查是否包含抖音登录所需的关键cookies
            required_cookies = ['sessionid', 'sessionid_ss', 'passport_csrf_token', 'sid_guard']
            has_login_cookies = any(cookie.get('name') in required_cookies for cookie in valid_cookies)
            
            # 如果没有登录cookies，即使有其他cookies也认为无效
            return has_login_cookies
        except Exception:
            return False
    
    def perform_login(self):
        """执行登录流程"""
        try:
            # 导入登录模块
            from manual_login import manual_login_and_save_cookie
            import asyncio
            
            # 运行登录函数
            asyncio.run(manual_login_and_save_cookie())
            
            # 检查登录是否成功（cookie文件是否存在且包含关键cookies）
            if os.path.exists("douyin_cookies.json"):
                # 验证 cookies 是否包含登录所需的关键信息
                try:
                    with open("douyin_cookies.json", 'r', encoding='utf-8') as f:
                        cookies = json.load(f)
                    
                    required_cookies = ['sessionid', 'sessionid_ss', 'passport_csrf_token', 'sid_guard']
                    has_login_cookies = any(cookie.get('name') in required_cookies for cookie in cookies)
                    
                    if has_login_cookies:
                        messagebox.showinfo("登录成功", "抖音账号登录成功！")
                        return True
                    else:
                        messagebox.showwarning("登录警告", "登录可能未完成，缺少关键登录信息。请确保已成功登录抖音账号。")
                        return False
                except Exception as e:
                    messagebox.showerror("登录错误", f"验证登录状态时出现错误：{str(e)}")
                    return False
            else:
                messagebox.showerror("登录失败", "登录未成功，请重试。")
                return False
        except Exception as e:
            messagebox.showerror("登录错误", f"登录过程中出现错误：{str(e)}")
            return False
            return False
    
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建笔记本控件（选项卡）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 视频处理选项卡
        self.create_video_tab(notebook)
        
        # 知识管理选项卡
        self.create_knowledge_tab(notebook)
        
        # 统计信息选项卡
        self.create_statistics_tab(notebook)
        
        # 设置选项卡
        self.create_settings_tab(notebook)
    
    def create_video_tab(self, notebook):
        """创建视频处理选项卡"""
        video_frame = ttk.Frame(notebook)
        notebook.add(video_frame, text="视频处理")
        
        # URL输入区域
        url_frame = ttk.LabelFrame(video_frame, text="视频URL")
        url_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(url_frame, text="视频链接:").pack(side=tk.LEFT, padx=5, pady=5)
        self.url_entry = ttk.Entry(url_frame, width=80)
        self.url_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.url_entry.bind("<Return>", lambda e: self.start_video_processing())
        
        ttk.Button(url_frame, text="添加", command=self.start_video_processing).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 进度和控制区域
        progress_frame = ttk.LabelFrame(video_frame, text="处理进度")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5, expand=True)
        
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack(pady=5)
        
        # 控制按钮
        control_frame = ttk.Frame(video_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.process_btn = ttk.Button(control_frame, text="开始处理", command=self.start_video_processing)
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(control_frame, text="取消", command=self.cancel_processing, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(video_frame, text="处理结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_knowledge_tab(self, notebook):
        """创建知识管理选项卡"""
        knowledge_frame = ttk.Frame(notebook)
        notebook.add(knowledge_frame, text="知识管理")
        
        # 搜索区域
        search_frame = ttk.LabelFrame(knowledge_frame, text="搜索知识")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="关键词:").pack(side=tk.LEFT, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", lambda e: self.search_knowledge())
        
        ttk.Button(search_frame, text="搜索", command=self.search_knowledge).pack(side=tk.RIGHT, padx=5, pady=5)
        ttk.Button(search_frame, text="刷新", command=self.load_knowledge).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 知识列表
        list_frame = ttk.Frame(knowledge_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建树形视图
        columns = ('ID', '标题', '分类', '重要性', '创建时间')
        self.knowledge_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.knowledge_tree.heading(col, text=col)
            self.knowledge_tree.column(col, width=100)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.knowledge_tree.yview)
        self.knowledge_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.knowledge_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.knowledge_tree.bind('<Double-1>', self.on_knowledge_select)
        
        # 知识详情区域
        detail_frame = ttk.LabelFrame(knowledge_frame, text="知识详情")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_statistics_tab(self, notebook):
        """创建统计信息选项卡"""
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="统计信息")
        
        # 统计信息显示区域
        stats_display_frame = ttk.LabelFrame(stats_frame, text="统计数据")
        stats_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_display_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 系统监控信息
        system_frame = ttk.LabelFrame(stats_frame, text="系统监控")
        system_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 创建系统监控标签
        self.cpu_label = ttk.Label(system_frame, text="CPU: --%")
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.memory_label = ttk.Label(system_frame, text="内存: --%")
        self.memory_label.pack(side=tk.LEFT, padx=10)
        
        self.disk_label = ttk.Label(system_frame, text="磁盘: --%")
        self.disk_label.pack(side=tk.LEFT, padx=10)
        
        self.network_label = ttk.Label(system_frame, text="网络: -- KB/s")
        self.network_label.pack(side=tk.LEFT, padx=10)
    
    def create_settings_tab(self, notebook):
        """创建设置选项卡"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="设置")
        
        # AI设置
        ai_frame = ttk.LabelFrame(settings_frame, text="AI设置")
        ai_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ai_frame, text="AI提供商:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_provider_var = tk.StringVar(value=config_manager.get("ai.provider", "openai"))
        ai_provider_combo = ttk.Combobox(ai_frame, textvariable=self.ai_provider_var, 
                                        values=["openai", "anthropic", "local"])
        ai_provider_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(ai_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_model_var = tk.StringVar(value=config_manager.get("ai.model", "gpt-3.5-turbo"))
        ai_model_entry = ttk.Entry(ai_frame, textvariable=self.ai_model_var, width=30)
        ai_model_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(ai_frame, text="API密钥:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.ai_api_key_var = tk.StringVar(value=config_manager.get("ai.api_key", ""))
        ai_api_key_entry = ttk.Entry(ai_frame, textvariable=self.ai_api_key_var, width=50, show="*")
        ai_api_key_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 视频设置
        video_frame = ttk.LabelFrame(settings_frame, text="视频设置")
        video_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(video_frame, text="视频质量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.video_quality_var = tk.StringVar(value=config_manager.get("video.video_quality", "720p"))
        video_quality_combo = ttk.Combobox(video_frame, textvariable=self.video_quality_var,
                                          values=["360p", "480p", "720p", "1080p"])
        video_quality_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 数据目录设置
        data_frame = ttk.LabelFrame(settings_frame, text="数据目录")
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(data_frame, text="数据库路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.db_path_var = tk.StringVar(value=config_manager.get("database.db_path", "./data/knowledge.db"))
        db_path_entry = ttk.Entry(data_frame, textvariable=self.db_path_var, width=50)
        db_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 保存设置按钮
        ttk.Button(settings_frame, text="保存设置", command=self.save_settings).pack(pady=10)
    
    def update_system_metrics(self, metrics: 'SystemMetrics'):
        """更新系统监控指标"""
        self.cpu_label.config(text=f"CPU: {metrics.cpu_percent:.1f}%")
        self.memory_label.config(text=f"内存: {metrics.memory_percent:.1f}%")
        self.disk_label.config(text=f"磁盘: {metrics.disk_usage_percent:.1f}%")
        
        # 计算网络速度
        current_network = {
            'bytes_recv': metrics.network_bytes_recv,
            'bytes_sent': metrics.network_bytes_sent
        }
        network_speed = 0
        if hasattr(self, '_last_network_metrics'):
            last_network = self._last_network_metrics
            bytes_received_diff = current_network['bytes_recv'] - last_network['bytes_recv']
            bytes_sent_diff = current_network['bytes_sent'] - last_network['bytes_sent']
            time_diff = (metrics.timestamp - self._last_metrics_timestamp).total_seconds()
            if time_diff > 0:
                network_speed = ((bytes_received_diff + bytes_sent_diff) / 1024) / time_diff  # KB/s
        
        self.network_label.config(text=f"网络: {network_speed:.1f} KB/s")
        self._last_network_metrics = current_network.copy()
        self._last_metrics_timestamp = metrics.timestamp
    
    def start_video_processing(self):
        """开始视频处理"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入视频URL")
            return
        
        # 禁用开始按钮，启用取消按钮
        self.process_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.is_processing = True
        
        # 在新线程中处理视频
        self.processing_thread = threading.Thread(target=self.process_video_thread, args=(url,))
        self.processing_thread.start()
    
    def process_video_thread(self, url: str):
        """视频处理线程"""
        try:
            # 检查用户是否已登录抖音
            if not self.is_logged_in():
                result = messagebox.askyesno("登录提示", "您尚未登录抖音账号，需要先进行登录才能获取视频信息。是否立即登录？")
                if result:
                    login_success = self.perform_login()
                    if not login_success:
                        self.update_status("登录失败，无法获取视频信息")
                        return
                else:
                    self.update_status("需要登录后才能获取视频信息")
                    return
            
            self.update_status("正在获取视频信息...")
            self.update_progress(10)
            
            # 获取视频信息（使用cookies）
            import asyncio
            video_info = asyncio.run(self.video_acquisition.get_video_info(url, use_cookies=True))
            if not video_info:
                self.update_status("获取视频信息失败")
                return
            
            self.current_video_info = video_info
            
            # 检查视频是否已存在
            existing_video = self.db_manager.get_video_by_platform_id(video_info['platform'], video_info['video_id'])
            
            if existing_video:
                # 视频已存在，检查文件是否存在
                video_id = existing_video['id']
                video_filename = f"{existing_video['title']}.mp4"
                video_path = f"{self.video_acquisition.config.download_dir}/{video_filename}"
                
                # 检查转录文本是否存在
                existing_transcript = self.db_manager.get_transcript_by_video_id(video_id)
                
                if existing_transcript:
                    # 转录文本已存在，直接使用
                    text = existing_transcript['content']
                    self.update_status("使用已存在的转录文本...")
                    self.update_progress(50)
                elif os.path.exists(video_path):
                    # 视频文件存在但转录文本不存在，提取音频
                    self.update_status("使用已下载的视频，正在提取音频...")
                    self.update_progress(40)
                    
                    text = self.video_processor.process_video(video_path)
                    if not text:
                        self.update_status("视频处理失败")
                        return
                    
                    # 保存转录文本
                    self.db_manager.insert_transcript(video_id, text)
                else:
                    # 视频文件不存在，重新下载
                    self.update_status("视频文件不存在，正在重新下载...")
                    self.update_progress(30)
                    
                    download_path = asyncio.run(self.video_acquisition.download_video_by_info(
                        video_info, 
                        self.video_acquisition.config.download_dir,
                        use_cookies=True
                    ))
                    
                    if not download_path:
                        self.update_status("视频下载失败")
                        return
                    
                    # 更新数据库状态
                    self.db_manager.update_video_status(video_id, 'downloaded')
                    
                    # 处理视频（提取音频并转换为文本）
                    text = self.video_processor.process_video(download_path)
                    if not text:
                        self.update_status("视频处理失败")
                        return
                    
                    # 保存转录文本
                    self.db_manager.insert_transcript(video_id, text)
            else:
                # 视频不存在，插入新记录
                video_id = self.db_manager.insert_video(
                    platform=video_info['platform'],
                    video_id=video_info['video_id'],
                    title=video_info['title'],
                    author=video_info['author'],
                    url=video_info['url'],
                    duration=video_info.get('duration'),
                    status='downloading'
                )
                
                self.update_status("正在下载视频...")
                self.update_progress(30)
                
                # 下载视频（使用cookies）
                download_path = asyncio.run(self.video_acquisition.download_video_by_info(
                    video_info, 
                    self.video_acquisition.config.download_dir,
                    use_cookies=True
                ))
                
                if not download_path:
                    self.update_status("视频下载失败")
                    return
                
                # 更新数据库状态
                self.db_manager.update_video_status(video_id, 'downloaded')
                
                self.update_status("正在提取音频...")
                self.update_progress(50)
                
                # 处理视频（提取音频并转换为文本）
                text = self.video_processor.process_video(download_path)
                if not text:
                    self.update_status("视频处理失败")
                    self.logger.error("视频处理失败，无法提取文本")
                    return
                
                # 保存转录文本
                self.db_manager.insert_transcript(video_id, text)
                self.logger.info(f"转录文本已保存，长度: {len(text)} 字符")
            
            self.update_status("正在分析内容...")
            self.update_progress(70)
            
            # 使用AI分析内容
            self.logger.info("开始 AI 分析...")
            knowledge_points = self.ai_analyzer.extract_knowledge_points(text)
            self.logger.info(f"AI 分析完成，提取到 {len(knowledge_points)} 个知识点")
            
            # 精炼知识点
            refined_knowledge = KnowledgeRefiner.refine_knowledge(knowledge_points)
            self.logger.info(f"知识点精炼完成，精炼后数量: {len(refined_knowledge)}")
            
            self.update_status("正在保存知识...")
            self.update_progress(90)
            
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
            
            self.knowledge_manager.add_knowledge_batch(knowledge_list)
            
            # 更新视频状态
            self.db_manager.update_video_status(video_id, 'processed')
            
            self.update_status("处理完成!")
            self.update_progress(100)
            
            # 显示结果
            self.show_processing_result(refined_knowledge)
            
        except Exception as e:
            self.update_status(f"处理出错: {str(e)}")
        finally:
            self.process_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.DISABLED)
            self.is_processing = False
    
    def cancel_processing(self):
        """取消处理"""
        self.is_processing = False
        self.update_status("处理已取消")
        self.process_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
    
    def update_status(self, status: str):
        """更新状态标签"""
        self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def update_progress(self, value: int):
        """更新进度条"""
        self.progress_bar['value'] = value
        self.root.update_idletasks()
    
    def show_processing_result(self, knowledge_points: List[Dict[str, Any]]):
        """显示处理结果"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        if knowledge_points:
            for i, kp in enumerate(knowledge_points, 1):
                self.result_text.insert(tk.END, f"知识点 {i}:\n")
                self.result_text.insert(tk.END, f"标题: {kp['title']}\n")
                self.result_text.insert(tk.END, f"内容: {kp['content'][:200]}...\n")
                self.result_text.insert(tk.END, f"分类: {kp['category']}\n")
                self.result_text.insert(tk.END, f"标签: {', '.join(kp['tags'])}\n")
                self.result_text.insert(tk.END, f"重要性: {kp['importance']}\n")
                self.result_text.insert(tk.END, "-" * 50 + "\n")
        else:
            self.result_text.insert(tk.END, "未提取到知识点")
        
        self.result_text.config(state=tk.DISABLED)
    
    def search_knowledge(self):
        """搜索知识"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("警告", "请输入搜索关键词")
            return
        
        results = self.knowledge_manager.search_knowledge(query)
        
        # 清空现有项目
        for item in self.knowledge_tree.get_children():
            self.knowledge_tree.delete(item)
        
        # 添加搜索结果
        for result in results:
            self.knowledge_tree.insert('', tk.END, values=(
                result['id'],
                result['title'][:30] + "..." if len(result['title']) > 30 else result['title'],
                result['category'] or '未分类',
                result['importance'],
                result['created_at']
            ))
    
    def on_knowledge_select(self, event):
        """选择知识条目时的处理"""
        selection = self.knowledge_tree.selection()
        if not selection:
            return
        
        item = self.knowledge_tree.item(selection[0])
        knowledge_id = item['values'][0]
        
        # 获取知识详情
        knowledge = self.knowledge_manager.get_knowledge_by_id(knowledge_id)
        if knowledge:
            self.show_knowledge_detail(knowledge)
    
    def show_knowledge_detail(self, knowledge: Dict[str, Any]):
        """显示知识详情"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        self.detail_text.insert(tk.END, f"标题: {knowledge['title']}\n")
        self.detail_text.insert(tk.END, f"分类: {knowledge['category'] or '未分类'}\n")
        self.detail_text.insert(tk.END, f"重要性: {knowledge['importance']}\n")
        self.detail_text.insert(tk.END, f"来源视频: {knowledge.get('video_title', '未知')}\n")
        self.detail_text.insert(tk.END, f"创建时间: {knowledge['created_at']}\n")
        self.detail_text.insert(tk.END, f"更新时间: {knowledge['updated_at']}\n")
        self.detail_text.insert(tk.END, f"标签: {', '.join(knowledge['tags'])}\n\n")
        self.detail_text.insert(tk.END, "内容:\n")
        self.detail_text.insert(tk.END, knowledge['content'])
        
        self.detail_text.config(state=tk.DISABLED)
    
    def load_knowledge(self):
        """加载所有知识点到列表"""
        try:
            # 清空现有项目
            for item in self.knowledge_tree.get_children():
                self.knowledge_tree.delete(item)
            
            # 获取所有知识点
            knowledge_list = self.knowledge_manager.get_all_knowledge()
            
            # 添加到树形视图
            for knowledge in knowledge_list:
                self.knowledge_tree.insert('', tk.END, values=(
                    knowledge['id'],
                    knowledge['title'][:30] + "..." if len(knowledge['title']) > 30 else knowledge['title'],
                    knowledge['category'] or '未分类',
                    knowledge['importance'],
                    knowledge['created_at']
                ))
            
            self.logger.info(f"已加载 {len(knowledge_list)} 条知识点")
        except Exception as e:
            self.logger.error(f"加载知识点失败: {e}")
            messagebox.showerror("错误", f"加载知识点失败: {str(e)}")
    
    def load_statistics(self):
        """加载统计信息"""
        stats = self.knowledge_manager.get_knowledge_statistics()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "知识库统计信息\n")
        self.stats_text.insert(tk.END, "=" * 50 + "\n")
        self.stats_text.insert(tk.END, f"总视频数: {stats['total_videos']}\n")
        self.stats_text.insert(tk.END, f"已处理视频: {stats['processed_videos']}\n")
        self.stats_text.insert(tk.END, f"知识条目总数: {stats['total_knowledge']}\n")
        self.stats_text.insert(tk.END, f"待复习知识: {stats['pending_reviews']}\n\n")
        
        self.stats_text.insert(tk.END, "分类统计:\n")
        for category, count in stats['top_categories']:
            self.stats_text.insert(tk.END, f"  {category}: {count}\n")
        
        self.stats_text.insert(tk.END, "\n重要性分布:\n")
        for item in stats['importance_distribution']:
            self.stats_text.insert(tk.END, f"  重要性 {item['importance']}: {item['count']} 条\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 更新配置
            config_manager.set("ai.provider", self.ai_provider_var.get())
            config_manager.set("ai.model", self.ai_model_var.get())
            config_manager.set("ai.api_key", self.ai_api_key_var.get())
            config_manager.set("video.video_quality", self.video_quality_var.get())
            config_manager.set("database.db_path", self.db_path_var.get())
            
            messagebox.showinfo("提示", "设置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()

# 使用示例
def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()