"""
抖音手动登录脚本 - 用于获取登录后的cookies
使用方法：
1. 运行此脚本：python manual_login.py
2. 脚本会打开浏览器并访问抖音网页版
3. 在浏览器中完成登录（扫码或手机号）
4. 登录成功后，按回车键保存cookies
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_douyin_cookies():
    """获取抖音登录后的cookies"""
    
    # 配置Chrome浏览器选项
    chrome_options = Options()
    
    # 设置用户代理，模拟真实浏览器
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 禁用自动化标识
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 添加更多反检测参数
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    
    # 如果需要看到浏览器界面，注释掉下面这行
    # chrome_options.add_argument('--headless')
    
    # 初始化WebDriver
    print("正在启动浏览器...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 访问抖音网页版
        print("正在打开抖音网页版...")
        driver.get("https://www.douyin.com/")
        
        # 等待页面加载
        time.sleep(3)
        
        print("\n" + "=" * 60)
        print("请在浏览器中完成以下操作：")
        print("1. 点击页面上的登录按钮")
        print("2. 选择登录方式（扫码或手机号）")
        print("3. 完成登录操作")
        print("4. 登录成功后，返回此终端按回车键保存cookies")
        print("=" * 60)
        print("\n等待登录完成...")
        
        # 等待用户按回车键
        input("\n登录成功后，请按回车键继续...")
        
        # 获取cookies
        print("正在获取cookies...")
        cookies = driver.get_cookies()
        
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
        
        return cookies
        
    except Exception as e:
        print(f"\n✗ 获取cookies失败: {e}")
        return None
    finally:
        # 关闭浏览器
        print("\n正在关闭浏览器...")
        driver.quit()


def main():
    """主函数"""
    print("=" * 60)
    print("抖音Cookies获取工具")
    print("=" * 60)
    print()
    
    # 检查是否已安装selenium和webdriver-manager
    try:
        import selenium
        import webdriver_manager
    except ImportError as e:
        print("错误: 缺少必要的依赖库")
        print("请运行以下命令安装:")
        print("pip install selenium webdriver-manager")
        return
    
    # 获取cookies
    cookies = get_douyin_cookies()
    
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