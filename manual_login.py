"""
手动获取抖音 cookies 的简化脚本
使用浏览器访问抖音页面，等待用户手动登录后保存 cookies
"""
import asyncio
import json
from playwright.async_api import async_playwright

async def manual_login_and_save_cookie():
    """
    步骤：
    1. 启动浏览器，打开抖音页面。
    2. 等待用户手动登录（扫码或手机号）。
    3. 登录成功后，按回车键保存Cookies到文件。
    """
    async with async_playwright() as p:
        print("正在启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-blink-features',
                '--disable-extensions',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        try:
            print("正在打开抖音页面...")
            await page.goto('https://www.douyin.com', wait_until='domcontentloaded')
            
            print("\n" + "=" * 60)
            print("请在浏览器中完成登录操作：")
            print("1. 点击登录按钮")
            print("2. 使用手机抖音APP扫码登录")
            print("3. 登录成功后，在此终端按回车键保存 cookies")
            print("=" * 60)
            
            # 等待用户按回车键
            input("\n按回车键保存 cookies...")
            
            # 保存 cookies
            print("\n正在保存 cookies...")
            cookies = await context.cookies()
            
            # 验证 cookies
            required_cookies = ['sessionid', 'sessionid_ss', 'passport_csrf_token', 'sid_guard']
            has_login_cookies = any(cookie.get('name') in required_cookies for cookie in cookies)
            
            if has_login_cookies:
                print(f"✓ Cookies 包含登录所需的关键信息")
                print(f"  找到的关键 cookies: {[c.get('name') for c in cookies if c.get('name') in required_cookies]}")
            else:
                print(f"⚠ 警告：Cookies 可能不包含登录所需的关键信息")
                print(f"  缺少的关键 cookies: {required_cookies}")
                print(f"  当前 cookies 数量: {len(cookies)}")
                print(f"  当前 cookies 名称: {[c.get('name') for c in cookies]}")
            
            with open('douyin_cookies.json', 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Cookies 已成功保存至文件: douyin_cookies.json")
            
            # 显示 cookies 信息
            print(f"\nCookies 信息：")
            print(f"  总数量: {len(cookies)}")
            print(f"  Cookie 名称列表:")
            for cookie in cookies:
                print(f"    - {cookie.get('name')}")
            
        except Exception as e:
            print(f"过程中出现错误: {e}")
        finally:
            print("\n浏览器将在 5 秒后关闭...")
            await asyncio.sleep(5)
            await browser.close()
            print("浏览器已关闭。")

if __name__ == '__main__':
    asyncio.run(manual_login_and_save_cookie())
