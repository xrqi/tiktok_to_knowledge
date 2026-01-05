import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000'

def monitor_task(task_id):
    """监控任务状态"""
    print(f"监控任务: {task_id}\n")
    
    for i in range(30):
        response = requests.get(f'{BASE_URL}/api/task/{task_id}')
        task_data = response.json()
        
        print(f"[{i+1}s] 状态: {task_data.get('status')} | 进度: {task_data.get('progress')}% | 消息: {task_data.get('message')}")
        
        if task_data.get('status') == 'completed':
            print(f"\n✓ 任务完成！结果: {task_data.get('result')}")
            return True
        elif task_data.get('status') == 'failed':
            print(f"\n✗ 任务失败！错误: {task_data.get('error')}")
            return False
        
        time.sleep(1)
    
    print("\n✗ 任务超时")
    return False

if __name__ == '__main__':
    # 创建一个测试任务
    test_url = "https://www.douyin.com/video/test123"
    
    print("创建测试任务...")
    response = requests.post(f'{BASE_URL}/api/analyze', json={'url': test_url})
    data = response.json()
    
    if data.get('success'):
        task_id = data.get('task_id')
        print(f"任务ID: {task_id}\n")
        monitor_task(task_id)
    else:
        print(f"任务创建失败: {data.get('error')}")
