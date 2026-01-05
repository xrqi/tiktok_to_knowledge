import psutil
import time
import threading
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    video_processing_queue_size: int = 0
    knowledge_extraction_queue_size: int = 0


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.monitoring = False
        self.monitoring_thread = None
        self.metrics_history = []
        self.max_history_size = 100  # 保留最近100个指标记录
        
        # 回调函数列表，用于在收集指标后执行自定义操作
        self.callbacks = []
        
    def start_monitoring(self, interval: float = 5.0):
        """开始监控系统资源
        
        Args:
            interval: 监控间隔（秒）
        """
        if self.monitoring:
            print("系统监控已在运行中")
            return
            
        self.monitoring = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        print(f"系统监控已启动，监控间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控系统资源"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        print("系统监控已停止")
    
    def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # 限制历史记录大小
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                # 执行回调函数
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        print(f"执行监控回调时出错: {e}")
                
                time.sleep(interval)
            except Exception as e:
                print(f"监控循环出错: {e}")
                if self.monitoring:
                    time.sleep(interval)
    
    def collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        # 获取CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 获取内存使用率
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        
        # 获取磁盘使用率
        disk_usage = psutil.disk_usage('/')
        disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        # 获取网络IO统计
        net_io = psutil.net_io_counters()
        network_bytes_sent = net_io.bytes_sent
        network_bytes_recv = net_io.bytes_recv
        
        # 获取进程数量
        process_count = len(psutil.pids())
        
        # 创建指标对象
        metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            process_count=process_count
        )
        
        return metrics
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """获取当前系统指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_average_metrics(self, last_n: int = 10) -> Optional[SystemMetrics]:
        """获取最近N个指标的平均值"""
        if not self.metrics_history:
            return None
            
        recent_metrics = self.metrics_history[-last_n:]
        if not recent_metrics:
            return None
            
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage_percent for m in recent_metrics) / len(recent_metrics)
        
        # 返回最近的时间戳
        latest = recent_metrics[-1]
        
        return SystemMetrics(
            timestamp=latest.timestamp,
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            disk_usage_percent=avg_disk,
            network_bytes_sent=latest.network_bytes_sent,
            network_bytes_recv=latest.network_bytes_recv,
            process_count=latest.process_count
        )
    
    def get_system_status(self) -> Dict[str, any]:
        """获取系统状态摘要"""
        current_metrics = self.get_current_metrics()
        avg_metrics = self.get_average_metrics()
        
        status = {
            "is_monitoring": self.monitoring,
            "history_size": len(self.metrics_history),
            "current": {},
            "average": {}
        }
        
        if current_metrics:
            status["current"] = {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "disk_usage_percent": current_metrics.disk_usage_percent,
                "process_count": current_metrics.process_count
            }
        
        if avg_metrics:
            status["average"] = {
                "cpu_percent": avg_metrics.cpu_percent,
                "memory_percent": avg_metrics.memory_percent,
                "disk_usage_percent": avg_metrics.disk_usage_percent
            }
        
        return status
    
    def add_callback(self, callback):
        """添加监控回调函数"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """移除监控回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def check_resource_thresholds(self, 
                                  cpu_threshold: float = 80.0,
                                  memory_threshold: float = 85.0,
                                  disk_threshold: float = 90.0) -> Dict[str, bool]:
        """检查资源是否超过阈值
        
        Args:
            cpu_threshold: CPU使用率阈值(%)
            memory_threshold: 内存使用率阈值(%)
            disk_threshold: 磁盘使用率阈值(%)
            
        Returns:
            包含各资源是否超过阈值的字典
        """
        current_metrics = self.get_current_metrics()
        if not current_metrics:
            return {"cpu": False, "memory": False, "disk": False}
        
        return {
            "cpu": current_metrics.cpu_percent > cpu_threshold,
            "memory": current_metrics.memory_percent > memory_threshold,
            "disk": current_metrics.disk_usage_percent > disk_threshold
        }


class ResourceUsageTracker:
    """资源使用跟踪器，用于跟踪特定任务的资源使用情况"""
    
    def __init__(self):
        self.start_time = None
        self.start_cpu_times = None
        self.start_memory = None
    
    def start_tracking(self):
        """开始跟踪资源使用"""
        self.start_time = time.time()
        self.start_cpu_times = psutil.Process().cpu_times()
        self.start_memory = psutil.Process().memory_info()
    
    def stop_tracking(self) -> Dict[str, any]:
        """停止跟踪并返回资源使用情况"""
        if not self.start_time:
            return {}
        
        end_time = time.time()
        end_cpu_times = psutil.Process().cpu_times()
        end_memory = psutil.Process().memory_info()
        
        duration = end_time - self.start_time
        cpu_user_time = end_cpu_times.user - self.start_cpu_times.user
        cpu_system_time = end_cpu_times.system - self.start_cpu_times.system
        memory_diff = end_memory.rss - self.start_memory.rss
        
        return {
            "duration_seconds": duration,
            "cpu_user_time": cpu_user_time,
            "cpu_system_time": cpu_system_time,
            "memory_bytes_diff": memory_diff,
            "memory_mb_diff": memory_diff / (1024 * 1024)
        }


# 使用示例和测试
if __name__ == "__main__":
    # 创建系统监控器实例
    monitor = SystemMonitor()
    
    # 定义一个简单的回调函数来处理指标
    def metrics_callback(metrics: SystemMetrics):
        print(f"[{metrics.timestamp.strftime('%H:%M:%S')}] "
              f"CPU: {metrics.cpu_percent:.1f}%, "
              f"Memory: {metrics.memory_percent:.1f}%, "
              f"Disk: {metrics.disk_usage_percent:.1f}%")
    
    # 添加回调函数
    monitor.add_callback(metrics_callback)
    
    # 开始监控
    monitor.start_monitoring(interval=2.0)  # 每2秒收集一次指标
    
    # 运行一段时间后停止
    try:
        time.sleep(10)  # 监控10秒
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop_monitoring()
    
    # 打印系统状态摘要
    status = monitor.get_system_status()
    print("\n系统状态摘要:")
    print(f"监控状态: {'运行中' if status['is_monitoring'] else '已停止'}")
    print(f"历史记录数量: {status['history_size']}")
    print(f"当前CPU使用率: {status['current'].get('cpu_percent', 'N/A')}%")
    print(f"当前内存使用率: {status['current'].get('memory_percent', 'N/A')}%")
    print(f"平均CPU使用率: {status['average'].get('cpu_percent', 'N/A')}%")
    print(f"平均内存使用率: {status['average'].get('memory_percent', 'N/A')}%")
    
    # 测试资源使用跟踪器
    print("\n测试资源使用跟踪器:")
    tracker = ResourceUsageTracker()
    tracker.start_tracking()
    
    # 模拟一些计算工作
    sum(i * i for i in range(1000000))
    
    usage = tracker.stop_tracking()
    print(f"执行时间: {usage['duration_seconds']:.2f}秒")
    print(f"内存使用变化: {usage['memory_mb_diff']:.2f}MB")