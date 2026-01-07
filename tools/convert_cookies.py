"""
将表格格式的cookies转换为JSON格式
"""

import json
import re

# 从浏览器复制的cookies表格数据
cookies_text = """
SelfTabRedDotControl	%5B%7B%22id%22%3A%227468213134176553023%22%2C%22u%22%3A14%2C%22c%22%3A14%7D%2C%7B%22id%22%3A%227542024855206496290%22%2C%22u%22%3A19%2C%22c%22%3A19%7D%5D	.douyin.com	/	2027-01-07T12:45:42.916Z	173						Medium	
session_tlb_tag	sttt%7C11%7CgPBcRknf6QIgd_S3j37fJv________-gnBpxYyReN9YIDTa7eRBHv4w5fp9zslOfABz2KCDPkX4%3D	.douyin.com	/	2026-03-08T12:44:05.986Z	105	✓	✓	None			Medium	
sessionid	80f05c4649dfe9022077f4b78f7edf26	.douyin.com	/	2026-03-08T12:44:05.986Z	41	✓	✓				Medium	
sessionid_ss	80f05c4649dfe9022077f4b78f7edf26	.douyin.com	/	2026-03-08T12:44:05.986Z	44	✓	✓	None			Medium	
sid_guard	80f05c4649dfe9022077f4b78f7edf26%7C1767789844%7C5184000%7CSun%2C+08-Mar-2026+12%3A44%3A04+GMT	.douyin.com	/	2027-01-02T12:44:05.986Z	102	✓	✓				Medium	
sid_tt	80f05c4649dfe9022077f4b78f7edf26	.douyin.com	/	2026-03-08T12:44:05.986Z	38	✓	✓				Medium	
sid_ucp_v1	1.0.0-KDQ2MDA1N2NiYTFlY2M0ZDg2YTc0MmY1MDUwZDUwODQ4NDQ2M2IyYTcKIQidobDs0_XKBBCUqvnKBhjvMSAMMPywz-4FOAdA9AdIBBoCbHEiIDgwZjA1YzQ2NDlkZmU5MDIyMDc3ZjRiNzhmN2VkZjI2	.douyin.com	/	2026-03-08T12:44:05.986Z	168	✓	✓				Medium	
ssid_ucp_v1	1.0.0-KDQ2MDA1N2NiYTFlY2M0ZDg2YTc0MmY1MDUwZDUwODQ4NDQ2M2IyYTcKIQidobDs0_XKBBCUqvnKBhjvMSAMMPywz-4FOAdA9AdIBBoCbHEiIDgwZjA1YzQ2NDlkZmU5MDIyMDc3ZjRiNzhmN2VkZjI2	.douyin.com	/	2026-03-08T12:44:05.986Z	169	✓	✓	None			Medium	
strategyABtestKey	%221767715859.552%22	.douyin.com	/	2026-01-13T16:10:59.553Z	37						Medium	
stream_player_status_params	%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22	.douyin.com	/	2026-01-07T14:06:48.566Z	218						Medium	
stream_recommend_feed_params	%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A16%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22	.douyin.com	/	2026-01-14T12:45:42.581Z	350						Medium	
totalRecommendGuideTagCount	11	.douyin.com	/	2026-01-14T12:46:00.883Z	29						Medium	
tt_scid	YJrJHHV31hYkNaP09f0b8D.91Hat-lpFVpoK1v8gc.lhHkkwZJi31SniWAvt36.Bc4cb	mssdk.bytedance.com	/	2026-01-13T13:28:58.875Z	75	✓	✓	None			Medium	
ttcid	a0afc772b0a24fc2a2ef9034db92d4d121	mssdk.bytedance.com	/	2026-01-13T13:28:58.875Z	39	✓	✓	None			Medium	
ttwid	1%7CgJXzcsD7_5Hg_wGN9XV_kC8IQtZqO7YvZKCQLfXWAIw%7C1767106041%7C7f232853b46155cc0d936e6eb388b17cfad0e0c57b3ebe6417fa8084e4f9c6ab	.iesdouyin.com	/	2027-01-02T12:22:10.140Z	132	✓					Medium	
ttwid	1%7CbESBR2Ty5_retH_xHSWU7Xc3l4O_79Tm7BuEvdSVUD8%7C1752423668%7C9650a17a1455a3145a7dfe6af329f1932ccb9cb1a82d7174e47cfbba02807cbe	.bytedance.com	/	2026-07-13T16:21:07.983Z	132	✓	✓	None			Medium	
ttwid	1%7CCF5ZZYrmHCmcalKvU5T7zHOMaQj4r5J9dEpuuZF-944%7C1767789811%7C7461ad160f0e50186c945687b02807ab9e9495541ab1cb2596ce19c2a056fc78	.douyin.com	/	2027-01-02T12:45:39.397Z	132	✓	✓	None			Medium	
uid_tt	3d9bdd32011300a92db8210ac70a7ca5	.douyin.com	/	2026-03-08T12:44:05.986Z	38	✓	✓				Medium	
uid_tt_ss	3d9bdd32011300a92db8210ac70a7ca5	.douyin.com	/	2026-03-08T12:44:05.986Z	41	✓	✓	None			Medium	
UIFID	1b474bc7e0db9591e645dd8feb8c65aae4845018effd0c2743039a380ee64740da89ab1884692540817243355cc22217b5ff360a75b560a48ef9be7740c88034abc1a8f934d8e3caa63325c9c694dbe80033c90fcbe6faf9a43a2338304343b1f060ce5b9e021086aff97cae2a3f878c3f8c863a5fdbd11928a57751fed186d4089ebeb5901d67bf124385c442e0200aae405e0f6f98f4cc869ef55381aab682	www.douyin.com	/	2026-09-11T14:41:00.598Z	325		✓				Medium	
UIFID_TEMP	1b474bc7e0db9591e645dd8feb8c65aae4845018effd0c2743039a380ee64740da89ab1884692540817243355cc222175c0d97f0e1e06dcc9a4b5b7278e2a763d2e913c349a4a4f525c76702a236590f	.douyin.com	/	2026-09-11T14:40:58.044Z	170		✓	None			Medium	
volume_info	%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.35%7D	.douyin.com	/	2027-02-10T15:54:59.829Z	86						Medium	
xg_device_score	7.873851705001503	www.douyin.com	/	Session	32						Medium	
xgplayer_device_id	40708059326	www.douyin.com	/	2026-08-07T14:45:40.768Z	29						Medium	
xgplayer_user_id	900254109496	www.douyin.com	/	2026-08-07T14:45:40.768Z	28						Medium	
"""

def parse_cookies_table(text):
    """解析表格格式的cookies"""
    cookies = []
    lines = text.strip().split('\n')
    
    for line in lines:
        # 使用制表符分割
        parts = line.split('\t')
        
        # 跳过空行或格式不正确的行
        if len(parts) < 5:
            continue
        
        # 提取cookie信息
        # 格式: Domain Name Value Path Expires Size HttpOnly Secure SameSite Priority
        # 但实际格式可能是: Domain Name Value Path Expires Size HttpOnly Secure SameSite Priority
        
        # 尝试解析
        if len(parts) >= 5:
            name = parts[0].strip()
            value = parts[1].strip()
            domain = parts[2].strip()
            path = parts[3].strip()
            expires_str = parts[4].strip()
            
            # 跳过没有名称的行
            if not name:
                continue
            
            # 解析过期时间
            expires = -1  # 默认为会话cookie
            if expires_str and expires_str != 'Session':
                try:
                    # 尝试解析ISO格式的时间
                    from datetime import datetime
                    dt = datetime.fromisoformat(expires_str.replace('Z', '+00:00'))
                    import time
                    expires = dt.timestamp()
                except:
                    pass
            
            # 解析HttpOnly和Secure标志
            httpOnly = False
            secure = False
            sameSite = 'Lax'
            
            if len(parts) >= 7:
                httpOnly = parts[5].strip() == '✓'
                secure = parts[6].strip() == '✓'
            
            if len(parts) >= 8:
                sameSite = parts[7].strip()
            
            # 创建cookie对象
            cookie = {
                'name': name,
                'value': value,
                'domain': domain,
                'path': path,
                'expires': expires,
                'httpOnly': httpOnly,
                'secure': secure,
                'sameSite': sameSite
            }
            
            cookies.append(cookie)
    
    return cookies

def main():
    """主函数"""
    print("=" * 60)
    print("Cookies转换工具")
    print("=" * 60)
    print()
    
    # 解析cookies
    cookies = parse_cookies_table(cookies_text)
    
    print(f"解析到 {len(cookies)} 个cookies")
    print()
    
    # 检查关键登录cookies
    required_cookies = ['sessionid', 'sessionid_ss', 'sid_guard', 'passport_csrf_token']
    found_cookies = [c for c in required_cookies if any(cookie['name'] == c for cookie in cookies)]
    
    print("关键登录cookies检查:")
    for cookie_name in required_cookies:
        found = any(cookie['name'] == cookie_name for cookie in cookies)
        status = "✓" if found else "✗"
        print(f"  {status} {cookie_name}")
    
    print()
    
    if not found_cookies:
        print("⚠️  警告: 未找到关键登录cookies！")
        print("   这些cookies可能不包含登录状态，可能无法访问需要登录的视频。")
        print("   请确保在浏览器中已经完成登录操作。")
        print()
    
    # 保存cookies到文件
    output_file = "douyin_cookies.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Cookies已保存到: {output_file}")
    print()
    
    # 显示部分cookies信息
    print("获取到的cookies包括:")
    for cookie in cookies[:10]:
        print(f"  - {cookie['name']}")
    if len(cookies) > 10:
        print(f"  ... 还有 {len(cookies) - 10} 个cookies")
    
    print()
    print("=" * 60)
    print("转换完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()