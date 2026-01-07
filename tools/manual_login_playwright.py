"""
抖音手动登录脚本 - 使用Playwright获取登录后的cookies
使用方法：
1. 运行此脚本：python manual_login_playwright.py
2. 脚本会打开浏览器并访问抖音网页版
3. 在浏览器中完成登录（扫码或手机号）
4. 登录成功后，按回车键保存cookies
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def get_douyin_cookies():
    """使用Playwright获取抖音登录后的cookies"""
    
    async with async_playwright() as p:
        # 启动Chromium浏览器
        print("正在启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-gpu'
            ]
        )
        
        # 创建新的浏览器上下文
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 创建新页面
        page = await context.new_page()
        
        try:
            # 访问抖音网页版
            print("正在打开抖音网页版...")
            await page.goto('https://www.douyin.com/', wait_until='networkidle')
            
            print("\n" + "=" * 60)
            print("请在浏览器中完成以下操作：")
            print("1. 点击页面上的登录按钮")
            print("2. 选择登录方式（扫码或手机号）")
            print("3. 完成登录操作")
            print("4. 登录成功后，返回此终端按回车键保存cookies")
            print("5. 等待时间：1分钟")
            print("=" * 60)
            print("\n等待登录完成...")
            print("提示：如果1分钟内未完成登录，请按Ctrl+C取消并重新运行")
            
            # 等待用户按回车键，最多等待60秒
            import time
            import threading
            
            user_input = []
            def get_input():
                try:
                    user_input.append(input("\n登录成功后，请按回车键继续..."))
                except:
                    pass
            
            # 启动输入线程
            input_thread = threading.Thread(target=get_input)
            input_thread.daemon = True
            input_thread.start()
            
            # 等待用户输入或超时
            start_time = time.time()
            timeout = 60  # 1分钟超时
            
            while input_thread.is_alive():
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed
                
                if elapsed >= timeout:
                    print("\n⚠ 超时：1分钟内未完成登录")
                    print("请按Ctrl+C取消，然后重新运行此脚本")
                    break
                
                # 每10秒显示一次倒计时
                if elapsed > 0 and elapsed % 10 == 0:
                    print(f"剩余时间: {remaining} 秒")
                
                time.sleep(1)
            
            # 如果线程还在运行，说明超时了
            if input_thread.is_alive():
                print("\n已超时，将保存当前cookies（可能不完整）")
            else:
                print("\n收到用户输入，继续保存cookies...")
            
            # 获取cookies
            print("正在获取cookies...")
            cookies = await context.cookies()
            
            # 保存cookies到文件
            cookies_file = "douyin_cookies.json"
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Cookies已保存到: {cookies_file}")
            print(f"✓ 共获取到 {len(cookies)} 个cookies")
            
            # 检查关键cookies
            required_cookies = ['sessionid', 'sessionid_ss', 'sid_guard', 'passport_csrf_token']
            found_cookies = [c for c in required_cookies if any(cookie['name'] == c for cookie in cookies)]
            
            if found_cookies:
                print(f"✓ 找到关键登录cookies: {', '.join(found_cookies)}")
            else:
                print("⚠ 警告: 未找到关键登录cookies，可能需要重新登录")
            
            # 显示部分cookies信息
            print("\n获取到的cookies包括:")
            for cookie in cookies[:10]:  # 只显示前10个
                print(f"  - {cookie['name']}")
            if len(cookies) > 10:
                print(f"  ... 还有 {len(cookies) - 10} 个cookies")
            
            return cookies
            
        except Exception as e:
            print(f"\n✗ 获取cookies失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 关闭浏览器
            print("\n正在关闭浏览器...")
            await browser.close()


def main():
    """主函数"""
    print("=" * 60)
    print("抖音Cookies获取工具 (Playwright版本)")
    print("=" * 60)
    print()
    
    # 检查是否已安装playwright
    try:
        import playwright
    except ImportError as e:
        print("错误: 缺少必要的依赖库")
        print("请运行以下命令安装:")
        print("pip install playwright")
        print("playwright install chromium")
        return
    
    # 运行异步函数
    cookies = asyncio.run(get_douyin_cookies())
    
    if cookies:
        print("\n" + "=" * 60)
        print("Cookies获取成功！")
        print("=" * 60)
        print("\n现在可以使用这些cookies来访问抖音视频了。")
        print("如果cookies过期，请重新运行此脚本获取新的cookies。")
    else:
        print("\n" + "=" * 60)
        print("Cookies获取失败！")
        print("=" * 60)
        print("\n请检查:")
        print("1. 是否正确完成了登录操作")
        print("2. 网络连接是否正常")
        print("3. 浏览器是否正常加载页面")


if __name__ == "__main__":
    main()