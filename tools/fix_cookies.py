"""
修复cookies格式问题
"""

import json

# 读取cookies文件
with open('douyin_cookies.json', 'r', encoding='utf-8') as f:
    cookies = json.load(f)

# 修复sameSite字段
for cookie in cookies:
    if cookie.get('sameSite') == '✓':
        cookie['sameSite'] = 'None'
    elif cookie.get('sameSite') == '':
        cookie['sameSite'] = 'Lax'

# 保存修复后的cookies
with open('douyin_cookies.json', 'w', encoding='utf-8') as f:
    json.dump(cookies, f, indent=2, ensure_ascii=False)

print("✓ Cookies格式已修复！")
print(f"✓ 共 {len(cookies)} 个cookies")

# 检查关键cookies
required_cookies = ['sessionid', 'sessionid_ss', 'sid_guard', 'passport_csrf_token']
print("\n关键cookies检查:")
for cookie_name in required_cookies:
    found = any(cookie['name'] == cookie_name for cookie in cookies)
    status = "✓" if found else "✗"
    print(f"  {status} {cookie_name}")

print("\n✓ Cookies已准备好使用！")
print("现在可以在web应用中测试视频分析功能了。")