import requests
import json
import time
import logging
import qrcode
import io
import base64
import os
import sys
import subprocess
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

from config.config_manager import get_config, update_user_cookies, get_user_cookies

class LoginManager:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': get_config('network.user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Referer': 'https://www.bilibili.com',
            'Origin': 'https://www.bilibili.com'
        })
        self.logger = logging.getLogger(__name__)
        
        # 设置代理
        proxy = get_config('network.proxy')
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
    
    def check_login_status(self) -> bool:
        """检查当前登录状态"""
        try:
            url = "https://api.bilibili.com/x/web-interface/nav"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('code') == 0 and data.get('data', {}).get('isLogin', False)
            return False
        except Exception as e:
            self.logger.error(f"检查登录状态失败: {e}")
            return False

    def verify_cookie_availability(self) -> Tuple[bool, Optional[str]]:
        """
        验证Cookie可用性并返回状态和消息
        
        Returns:
            Tuple[bool, Optional[str]]: (是否可用, 状态消息)
        """
        try:
            # 测试获取用户信息（需要登录的API）
            url = "https://api.bilibili.com/x/web-interface/nav"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    user_data = data.get('data', {})
                    if user_data.get('isLogin', False):
                        username = user_data.get('uname', '未知用户')
                        return True, f"Cookie有效 - 已登录用户: {username}"
                    else:
                        return False, "Cookie已失效，需要重新登录"
                else:
                    return False, f"Cookie验证失败: {data.get('message', '未知错误')}"
            else:
                return False, f"HTTP请求失败: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"Cookie验证异常: {e}")
            return False, f"Cookie验证异常: {str(e)}"
    
    def get_qrcode_login_url(self) -> Tuple[Optional[str], Optional[str]]:
        """获取二维码登录URL和oauthKey"""
        try:
            url = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    qrcode_url = data['data']['url']
                    oauth_key = data['data']['qrcode_key']
                    return qrcode_url, oauth_key
            return None, None
        except Exception as e:
            self.logger.error(f"获取二维码登录URL失败: {e}")
            return None, None
    
    def generate_qrcode_image(self, qrcode_url: str) -> Optional[str]:
        """生成二维码图片文件并返回文件路径"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qrcode_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 保存为文件
            qrcode_file = "qrcode.png"
            img.save(qrcode_file)
            
            # 尝试自动打开图片
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(qrcode_file)
                elif os.name == 'posix':  # macOS or Linux
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', qrcode_file])
                    else:  # Linux
                        subprocess.run(['xdg-open', qrcode_file])
            except Exception:
                self.logger.warning("无法自动打开二维码图片，请手动查看")
            
            return qrcode_file
        except Exception as e:
            self.logger.error(f"生成二维码失败: {e}")
            return None
    
    def check_qrcode_status(self, oauth_key: str) -> Tuple[bool, Optional[Dict]]:
        """检查二维码扫描状态"""
        try:
            url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
            params = {'qrcode_key': oauth_key}
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                code = data.get('code')
                
                if code == 0:  # 登录成功
                    # 提取Cookie
                    cookies = self._extract_cookies_from_response(response)
                    if cookies:
                        update_user_cookies(cookies)
                        return True, data
                elif code == 86101:  # 二维码未扫描
                    return False, None
                elif code == 86090:  # 二维码已扫描，等待确认
                    return False, None
                elif code == 86038:  # 二维码已过期
                    return False, {'expired': True}
            
            return False, None
        except Exception as e:
            self.logger.error(f"检查二维码状态失败: {e}")
            return False, None
    
    def password_login(self, username: str, password: str) -> bool:
        """账号密码登录（需要验证码处理，这里简化实现）"""
        # 注意：B站密码登录需要处理验证码，这里只提供框架
        self.logger.warning("密码登录功能需要处理验证码，建议使用二维码登录")
        return False
    
    def _extract_cookies_from_response(self, response: requests.Response) -> Dict[str, str]:
        """从响应中提取Cookie"""
        cookies = {}
        for cookie in response.cookies:
            if cookie.name in ['SESSDATA', 'bili_jct', 'DedeUserID', 'buvid3']:
                cookies[cookie.name] = cookie.value
        return cookies
    
    def set_cookies(self, cookies: Dict[str, str]) -> bool:
        """设置Cookie到session"""
        try:
            self.session.cookies.update(cookies)
            # 同时更新配置中的Cookie
            return update_user_cookies(cookies)
        except Exception as e:
            self.logger.error(f"设置Cookie失败: {e}")
            return False
    
    def get_session(self) -> requests.Session:
        """获取当前session"""
        return self.session
    
    def qrcode_login(self, timeout: int = 120) -> bool:
        """二维码登录流程"""
        print("开始二维码登录...")
        
        # 获取二维码
        qrcode_url, oauth_key = self.get_qrcode_login_url()
        if not qrcode_url or not oauth_key:
            print("获取二维码失败")
            return False
        
        # 生成并显示二维码
        qrcode_image = self.generate_qrcode_image(qrcode_url)
        if qrcode_image:
            print("请使用B站APP扫描二维码登录")
            print(f"二维码数据: {qrcode_image[:100]}...")  # 简化显示
        else:
            print(f"请手动打开链接: {qrcode_url}")
        
        # 轮询登录状态
        start_time = time.time()
        while time.time() - start_time < timeout:
            success, status_data = self.check_qrcode_status(oauth_key)
            
            if success:
                print("登录成功！")
                return True
            elif status_data and status_data.get('expired'):
                print("二维码已过期，重新生成...")
                return self.qrcode_login(timeout)
            
            print("等待扫描..." if not status_data else "已扫描，等待确认...")
            time.sleep(3)
        
        print("登录超时")
        return False

# 全局登录管理器实例
login_manager = LoginManager()

def init_login() -> bool:
    """初始化登录状态"""
    # 首先尝试使用配置中的Cookie
    cookies = get_user_cookies()
    if cookies:
        login_manager.set_cookies(cookies)
        if login_manager.check_login_status():
            print("使用保存的Cookie登录成功")
            return True
        else:
            print("保存的Cookie已失效")
    
    # 如果需要自动登录
    login_method = get_config('user.login_method', 'qrcode')
    if login_method == 'qrcode':
        success = login_manager.qrcode_login()
        if success:
            # 登录成功后，确保session包含最新的Cookie
            cookies = get_user_cookies()
            if cookies:
                login_manager.set_cookies(cookies)
        return success
    elif login_method == 'password':
        username = get_config('user.username')
        password = get_config('user.password')
        if username and password:
            success = login_manager.password_login(username, password)
            if success:
                # 登录成功后，确保session包含最新的Cookie
                cookies = get_user_cookies()
                if cookies:
                    login_manager.set_cookies(cookies)
            return success
    
    return False

def get_session() -> requests.Session:
    """获取登录session"""
    return login_manager.get_session()
