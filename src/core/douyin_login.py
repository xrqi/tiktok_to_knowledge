import asyncio
import json
from playwright.async_api import async_playwright

async def douyin_login_and_save_cookie():
    """
    步骤：
    1. 启动浏览器，打开抖音登录页。
    2. 等待并显示二维码（程序会暂停在此）。
    3. 您使用手机抖音APP扫码登录。
    4. 登录成功后，自动保存Cookies到文件。
    """
    # 启动Playwright和浏览器
    async with async_playwright() as p:
        print("正在启动浏览器...")
        # 使用 headed 模式以便您看到二维码
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
        # 设置更真实的浏览器上下文
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},  # 使用桌面视图
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # 隐藏 webdriver 特征
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        try:
            # 1. 导航到抖音网页版登录页
            print("正在打开抖音登录页面...")
            await page.goto('https://www.douyin.com', wait_until='domcontentloaded')
            
            # 等待页面加载完成，然后查找登录按钮
            print("查找登录入口...")
            # 尝试多种可能的登录按钮选择器
            login_selectors = [
                "text=登录",
                "[data-e2e='login-button']",
                ".login-btn",
                "button:text('登录')",
                "a:has-text('登录')",
                ".header-login-btn"
            ]
            
            login_found = False
            for selector in login_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=5000)
                    # 点击登录按钮
                    await page.click(selector)
                    print("已点击登录按钮")
                    login_found = True
                    break
                except Exception:
                    continue
            
            if not login_found:
                print("未找到登录按钮，尝试访问登录页面...")
                # 如果没找到登录按钮，直接访问登录页面
                await page.goto('https://www.douyin.com/login', wait_until='domcontentloaded')

            # 2. 等待并定位二维码图片元素，同时监控登录状态
            print("等待二维码加载...")
            
            # 在等待二维码的同时开始监控登录状态
            login_success = False
            max_qr_wait_time = 30  # 等待二维码最多30秒
            check_interval = 2     # 每2秒检查一次
            
            # 检查登录状态的函数
            async def check_login_status():
                # 检查URL是否已经变化（登录成功后通常会跳转）
                current_url = page.url
                if current_url != 'https://www.douyin.com/login' and 'douyin.com' in current_url and '/login' not in current_url:
                    return True
                
                # 检查页面上是否出现用户相关的元素（表示登录成功）
                user_elements = [
                    "[data-e2e='user-avatar']",
                    ".user-account",
                    "[data-e2e*='profile']",
                    ".user-profile",
                    ".account-avatar",
                    "img[alt*='头像']",
                    "[data-e2e*='account']"
                ]
                
                for element in user_elements:
                    try:
                        if await page.query_selector(element):
                            return True
                    except:
                        continue
                
                # 检查是否出现登录成功后的常见页面元素
                try:
                    if await page.query_selector("text=我的") or await page.query_selector("text=个人资料"):
                        return True
                except:
                    pass
                
                return False
            
            # 首先检查是否已经登录（避免等待二维码）
            login_success = await check_login_status()
            
            if not login_success:
                # 二维码选择器 - 尝试多种可能的选择器，因为页面结构可能变化
                qr_selectors = [
                    "img[src*='qrcode']",
                    "img[src*='qr_code']",
                    "img[alt*='二维码']",
                    "img[alt*='QR']",
                    ".qrcode img",
                    ".qr-code img",
                    "[data-e2e*='qrcode'] img",
                    ".web-login-qrcode img",
                    ".qrcode-common img",
                    "img[data-log*='qrcode']",
                    ".login-qrcode img"
                ]
                
                qr_code_found = False
                for selector in qr_selectors:
                    try:
                        await page.wait_for_selector(selector, state='visible', timeout=5000)
                        qr_code_selector = selector
                        qr_code_found = True
                        print("二维码已显示！请打开手机抖音APP扫描二维码进行登录。")
                        break
                    except Exception:
                        # 在等待二维码时继续检查登录状态
                        login_success = await check_login_status()
                        if login_success:
                            break
                        continue
                
                if not qr_code_found and not login_success:
                    # 如果常见选择器都没找到，尝试更通用的方法
                    print("正在尝试其他方式定位二维码...")
                    # 等待页面加载，然后查找可能的二维码元素
                    for i in range(max_qr_wait_time // check_interval):
                        # 在等待过程中持续检查登录状态
                        login_success = await check_login_status()
                        if login_success:
                            print("检测到登录成功，无需等待二维码！")
                            break
                        
                        try:
                            if await page.query_selector("text=扫码登录"):
                                # 如果找到扫码登录文本，尝试等待图片元素
                                await page.wait_for_selector("img", state='visible', timeout=check_interval*1000)
                                qr_code_found = True
                                print("二维码已显示！请打开手机抖音APP扫描二维码进行登录。")
                                break
                        except:
                            pass
                        
                        print(f"等待二维码中... ({(i+1) * check_interval}/{max_qr_wait_time} 秒)")
                        await asyncio.sleep(check_interval)
                    
                    if not qr_code_found and not login_success:
                        # 如果所有方法都失败，使用更通用的方法等待登录页面元素
                        print("正在加载登录页面，请稍候...")
                        qr_code_found = True  # 标记为找到，继续等待登录

            # 3. 如果尚未登录成功，继续等待扫码和登录
            if not login_success:
                print("等待您扫码登录... (程序将在此等待最多3分钟)")
                
                # 使用轮询机制检查登录状态，而不是等待URL变化
                max_wait_time = 180  # 3分钟 = 180秒
                check_interval = 2   # 每2秒检查一次
                
                for i in range(max_wait_time // check_interval):
                    try:
                        # 使用之前定义的检查函数
                        login_success = await check_login_status()
                        if login_success:
                            print("检测到登录成功！")
                            break
                        
                        print(f"等待登录中... ({(i+1) * check_interval}/{max_wait_time} 秒)")
                        await asyncio.sleep(check_interval)
                        
                    except Exception as e:
                        print(f"检查登录状态时出现异常: {e}")
                        await asyncio.sleep(check_interval)
                        continue
                
                if not login_success:
                    print("登录等待超时，可能需要手动完成验证步骤。")
                    # 给用户更多时间完成短信验证等步骤
                    additional_wait = 60  # 额外等待60秒
                    print(f"继续等待 {additional_wait} 秒以完成可能的验证步骤...")
                    for i in range(additional_wait):
                        login_success = await check_login_status()
                        if login_success:
                            print("检测到登录成功！")
                            break
                        await asyncio.sleep(1)
            else:
                print("登录状态已确认，跳过等待阶段。")

            # 4. 登录成功，保存Cookies
            if login_success:
                print("登录成功！正在保存登录状态(Cookies)...")
                cookies = await context.cookies()
                
                # 验证 cookies 是否包含关键的登录 cookies
                required_cookies = ['sessionid', 'sessionid_ss', 'passport_csrf_token', 'sid_guard']
                has_login_cookies = any(cookie.get('name') in required_cookies for cookie in cookies)
                
                if has_login_cookies:
                    print("✓ 验证成功：Cookies 包含登录所需的关键信息")
                    print(f"  找到的关键 cookies: {[c.get('name') for c in cookies if c.get('name') in required_cookies]}")
                else:
                    print("⚠ 警告：Cookies 不包含登录所需的关键信息")
                    print(f"  缺少的关键 cookies: {required_cookies}")
                    print(f"  当前 cookies 数量: {len(cookies)}")
                    print(f"  当前 cookies 名称: {[c.get('name') for c in cookies]}")
                
                # 将Cookies保存为JSON文件
                with open('douyin_cookies.json', 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                print(f"Cookies已成功保存至文件: douyin_cookies.json")

                # 可选：保持浏览器打开一段时间，供您确认
                await asyncio.sleep(5)
            else:
                print("登录未成功，未保存Cookies。")

        except Exception as e:
            print(f"过程中出现错误: {e}")
            print("可能的原因：二维码未出现、扫码超时或页面结构已更新。")
        finally:
            # 关闭浏览器
            try:
                await browser.close()
            except:
                pass  # 如果浏览器已经关闭，则忽略错误
            print("浏览器已关闭。")

# 运行主函数
if __name__ == '__main__':
    asyncio.run(douyin_login_and_save_cookie())