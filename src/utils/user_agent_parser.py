import re
from typing import Dict, Optional, Tuple


class UserAgentParser:
    """解析 User-Agent 字符串，提取设备、操作系统和浏览器信息"""
    
    @staticmethod
    def parse_user_agent(user_agent: str) -> Dict[str, Optional[str]]:
        """
        解析 User-Agent 字符串
        
        Args:
            user_agent: HTTP User-Agent 头部字符串
            
        Returns:
            包含 device_type, os_name, browser_name 的字典
        """
        if not user_agent:
            return {
                'device_type': 'unknown',
                'os_name': 'unknown',
                'browser_name': 'unknown'
            }
        
        device_type = UserAgentParser._detect_device_type(user_agent)
        os_name = UserAgentParser._detect_os(user_agent)
        browser_name = UserAgentParser._detect_browser(user_agent)
        
        return {
            'device_type': device_type,
            'os_name': os_name,
            'browser_name': browser_name
        }
    
    @staticmethod
    def _detect_device_type(user_agent: str) -> str:
        """检测设备类型"""
        user_agent_lower = user_agent.lower()
        
        # 检测移动设备
        mobile_patterns = [
            'mobile', 'android', 'iphone', 'ipod', 'ipad', 'blackberry',
            'windows phone', 'opera mini', 'iemobile', 'kindle'
        ]
        
        for pattern in mobile_patterns:
            if pattern in user_agent_lower:
                # 检测平板设备
                if 'ipad' in user_agent_lower or 'tablet' in user_agent_lower:
                    return 'tablet'
                return 'mobile'
        
        # 检测桌面设备
        desktop_patterns = ['windows', 'macintosh', 'linux', 'x11']
        for pattern in desktop_patterns:
            if pattern in user_agent_lower:
                return 'desktop'
        
        return 'unknown'
    
    @staticmethod
    def _detect_os(user_agent: str) -> str:
        """检测操作系统"""
        user_agent_lower = user_agent.lower()
        
        # Windows
        windows_match = re.search(r'windows\s+nt\s+(\d+\.\d+)', user_agent_lower)
        if windows_match:
            version = windows_match.group(1)
            version_map = {
                '10.0': 'Windows 10/11',
                '6.3': 'Windows 8.1',
                '6.2': 'Windows 8',
                '6.1': 'Windows 7',
                '6.0': 'Windows Vista',
                '5.1': 'Windows XP'
            }
            return version_map.get(version, 'Windows')
        
        if 'windows' in user_agent_lower:
            return 'Windows'
        
        # macOS
        if 'macintosh' in user_agent_lower or 'mac os x' in user_agent_lower:
            return 'macOS'
        
        # iOS
        if 'iphone' in user_agent_lower:
            return 'iOS (iPhone)'
        if 'ipad' in user_agent_lower:
            return 'iOS (iPad)'
        if 'ipod' in user_agent_lower:
            return 'iOS (iPod)'
        
        # Android
        android_match = re.search(r'android\s+(\d+\.?\d*)', user_agent_lower)
        if android_match:
            version = android_match.group(1)
            return f'Android {version}'
        
        if 'android' in user_agent_lower:
            return 'Android'
        
        # Linux
        if 'linux' in user_agent_lower and 'android' not in user_agent_lower:
            return 'Linux'
        
        # 其他
        if 'ubuntu' in user_agent_lower:
            return 'Ubuntu'
        if 'fedora' in user_agent_lower:
            return 'Fedora'
        if 'debian' in user_agent_lower:
            return 'Debian'
        
        return 'unknown'
    
    @staticmethod
    def _detect_browser(user_agent: str) -> str:
        """检测浏览器"""
        user_agent_lower = user_agent.lower()
        
        # Chrome (需要先检查，因为其他浏览器也可能包含 Chrome)
        chrome_match = re.search(r'chrome/(\d+\.?\d*)', user_agent_lower)
        if chrome_match and 'edg' not in user_agent_lower and 'opr' not in user_agent_lower:
            version = chrome_match.group(1)
            return f'Chrome {version}'
        
        # Edge
        edge_match = re.search(r'edg/(\d+\.?\d*)', user_agent_lower)
        if edge_match:
            version = edge_match.group(1)
            return f'Edge {version}'
        
        # Firefox
        firefox_match = re.search(r'firefox/(\d+\.?\d*)', user_agent_lower)
        if firefox_match:
            version = firefox_match.group(1)
            return f'Firefox {version}'
        
        # Safari
        if 'safari' in user_agent_lower and 'chrome' not in user_agent_lower:
            safari_match = re.search(r'version/(\d+\.?\d*)', user_agent_lower)
            if safari_match:
                version = safari_match.group(1)
                return f'Safari {version}'
            return 'Safari'
        
        # Opera
        opera_match = re.search(r'opr/(\d+\.?\d*)', user_agent_lower)
        if opera_match:
            version = opera_match.group(1)
            return f'Opera {version}'
        
        # IE
        if 'msie' in user_agent_lower or 'trident' in user_agent_lower:
            ie_match = re.search(r'(msie\s+(\d+\.?\d*)|rv:(\d+\.?\d*))', user_agent_lower)
            if ie_match:
                version = ie_match.group(2) or ie_match.group(3)
                return f'Internet Explorer {version}'
            return 'Internet Explorer'
        
        # 微信浏览器
        if 'micromessenger' in user_agent_lower:
            return 'WeChat Browser'
        
        # QQ浏览器
        if 'qqbrowser' in user_agent_lower:
            return 'QQ Browser'
        
        # UC浏览器
        if 'ucbrowser' in user_agent_lower:
            return 'UC Browser'
        
        return 'unknown'
    
    @staticmethod
    def get_client_ip(request) -> str:
        """
        从 Flask 请求对象中获取客户端 IP 地址
        
        Args:
            request: Flask request 对象
            
        Returns:
            客户端 IP 地址
        """
        # 检查代理头
        if request.headers.getlist("X-Forwarded-For"):
            return request.headers.getlist("X-Forwarded-For")[0]
        
        if request.headers.get("X-Real-IP"):
            return request.headers.get("X-Real-IP")
        
        # 直接连接
        return request.remote_addr or 'unknown'