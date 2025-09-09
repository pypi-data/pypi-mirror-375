"""
状态命令处理模块
处理状态检查相关的命令行功能
"""

from modules.login_manager import login_manager
from config.config_manager import get_user_cookies

def handle_status_command(args) -> int:
    """处理status子命令"""
    # 首先确保session包含最新的Cookie
    cookies = get_user_cookies()
    if cookies:
        login_manager.set_cookies(cookies)
    
    # 检查登录状态
    if login_manager.check_login_status():
        print("登录状态: 已登录 ✓")
        return 0
    else:
        print("登录状态: 未登录 ✗")
        print("请使用: bili-dl login 命令登录")
        return 1
