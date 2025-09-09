#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
B站视频下载器 - 模块化重构版本
功能：通过JSON配置控制登录 -> 获取最高清晰度视频 -> 自动合并DASH格式视频
"""

import argparse
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import init_config
from utils.common_utils import setup_logging
from commands import handle_download_command, handle_login_command, handle_status_command

def setup_argparse() -> argparse.ArgumentParser:
    """设置命令行参数解析"""
    parser = argparse.ArgumentParser(description='B站视频下载器')
    subparsers = parser.add_subparsers(dest='command', help='子命令', required=True)
    
    # download 子命令
    dl_parser = subparsers.add_parser('download', help='下载视频')
    dl_parser.add_argument('video_id', help='B站视频BV号或AV号，例如：BV1Ab411C7Q9 或 av123456789')
    dl_parser.add_argument('--output', '-o', default=None, help='输出目录')
    dl_parser.add_argument('--quality', '-q', type=int, default=None, help='指定清晰度（可选）')
    dl_parser.add_argument('--no-merge', action='store_true', help='不自动合并DASH视频')
    dl_parser.add_argument('--no-login', '--guest', action='store_true', 
                          help='忽略登录状态，使用游客模式下载（可能只能下载较低清晰度）')
    dl_parser.add_argument('--config', '-c', default='config/config.json', help='配置文件路径')
    dl_parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    # login 子命令
    login_parser = subparsers.add_parser('login', help='登录B站账号')
    login_parser.add_argument('--force', '-f', action='store_true', help='强制重新登录')
    login_parser.add_argument('--config', '-c', default='config/config.json', help='配置文件路径')
    login_parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    # status 子命令
    status_parser = subparsers.add_parser('status', help='检查登录状态')
    status_parser.add_argument('--config', '-c', default='config/config.json', help='配置文件路径')
    status_parser.add_argument('--debug', '-d', action='store_true', help='启用调试模式')
    
    return parser

def initialize_system(config_path: str, debug: bool = False) -> bool:
    """初始化系统配置"""
    try:
        # 设置日志
        log_level = "DEBUG" if debug else "INFO"
        setup_logging(level=log_level)
        
        # 初始化配置
        if not init_config():
            print("配置文件初始化失败")
            return False
        
        print("系统初始化完成")
        return True
        
    except Exception as e:
        print(f"系统初始化失败: {e}")
        return False


def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 初始化系统
    if not initialize_system(args.config, args.debug):
        return 1
    
    # 处理子命令
    if args.command == 'download':
        return handle_download_command(args)
    elif args.command == 'login':
        return handle_login_command(args)
    elif args.command == 'status':
        return handle_status_command(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
