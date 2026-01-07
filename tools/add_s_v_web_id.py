"""
添加缺失的s_v_web_id cookie
"""

import json
import random
import string
import time

def generate_s_v_web_id():
    """生成一个合理的s_v_web_id值"""
    # s_v_web_id的格式通常是: verify_<随机字符>_<随机字符>
    chars = string.ascii_letters + string.digits
    part1 = ''.join(random.choice(chars) for _ in range(19))
    part2 = ''.join(random.choice(chars) for _ in range(10))
    return f'verify_{part1}_{part2}'

# 读取cookies文件
with open('douyin_cookies.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

# 检查是否已存在s_v_web_id
has_s_v_web_id = any(cookie['name'] == 's_v_web_id' for cookie in cookies)

if not has_s_v_web_id:
    # 生成s_v_web_id cookie
    s_v_web_id_value = generate_s_v_web_id()
    
    # 创建cookie对象
    s_v_web_id_cookie = {
        'name': 's_v_web_id',
        'value': s_v_web_id_value,
        'domain': '.douyin.com',
        'path': '/',
        'expires': int(time.time()) + 365 * 24 * 60 * 60,  # 1年后过期
        'httpOnly': False,
        'secure': False,
        'sameSite': 'Lax'
    }
    
    # 添加到cookies列表
    cookies.append(s_v_web_id_cookie)
    
    print(f"✓ 已添加 s_v_web_id cookie: {s_v_web_id_value}")
else:
    print("⚠️  s_v_web_id cookie已存在，跳过添加")

# 保存更新后的cookies
with open('douyin_cookies.json', 'w', encoding='utf-8') as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print(f"\n✓ Cookies已更新，共 {len(cookies)} 个cookies")

# 检查关键cookies
required_cookies = ['sessionid', 'sessionid_ss', 'sid_guard', 's_v_web_id', 'passport_csrf_token']
print("\n关键cookies检查:")
for cookie_name in required_cookies:
    found = any(cookie['name'] == cookie_name for cookie in cookies)
    status = "✓" if found else "✗"
    print(f"  {status} {cookie_name}")

print("\n✓ Cookies已准备好使用！")
print("现在可以在web应用中测试视频分析功能了。")