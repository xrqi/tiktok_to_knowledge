import sqlite3

def get_video_urls():
    conn = sqlite3.connect('./data/knowledge.db')
    cursor = conn.cursor()
    
    print("=== 获取数据库中的视频URL ===\n")
    
    cursor.execute("SELECT id, platform, video_id, url, title FROM videos")
    videos = cursor.fetchall()
    
    for v in videos:
        print(f"[{v[0]}] {v[4]}")
        print(f"    平台: {v[1]}")
        print(f"    视频ID: {v[2]}")
        print(f"    URL: {v[3]}")
        print()
    
    conn.close()

if __name__ == '__main__':
    get_video_urls()
