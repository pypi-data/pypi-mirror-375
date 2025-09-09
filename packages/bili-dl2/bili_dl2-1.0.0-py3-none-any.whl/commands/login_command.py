"""
登录命令处理模块
处理登录相关的命令行功能
"""

from config.config_manager import set_config
from modules.login_manager import init_login

def handle_login_command(args) -> int:
    """处理login子命令"""
    if args.force:
        print("强制重新登录...")
        # 清除现有Cookie
        set_config('user.cookies', {})
    
    if init_login():
        print("登录成功！")
        return 0
    else:
        print("登录失败")
        return 1
