import json
import os
from typing import Dict, Any, Optional
import logging

class ConfigManager:
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_config(self) -> bool:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_path):
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                return False
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.logger.info("配置文件加载成功")
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            return False
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def save_config(self) -> bool:
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("配置文件保存成功")
            return True
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        keys = key.split('.')
        config_ref = self.config
        
        # 遍历到最后一个键之前
        for k in keys[:-1]:
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        # 设置最后一个键的值
        config_ref[keys[-1]] = value
        return self.save_config()
    
    def get_user_cookies(self) -> Dict[str, str]:
        """获取用户Cookie"""
        cookies = self.get('user.cookies', {})
        return {k: v for k, v in cookies.items() if v}  # 过滤空值
    
    def update_user_cookies(self, cookies: Dict[str, str]) -> bool:
        """更新用户Cookie"""
        current_cookies = self.get('user.cookies', {})
        current_cookies.update(cookies)
        return self.set('user.cookies', current_cookies)
    
    def get_download_config(self) -> Dict[str, Any]:
        """获取下载配置"""
        return self.get('download', {})
    
    def get_ffmpeg_config(self) -> Dict[str, Any]:
        """获取ffmpeg配置"""
        return self.get('ffmpeg', {})
    
    def get_network_config(self) -> Dict[str, Any]:
        """获取网络配置"""
        return self.get('network', {})
    
    def create_default_config(self) -> bool:
        """创建默认配置文件"""
        default_config = {
            "user": {
                "username": "",
                "password": "",
                "cookies": {
                    "SESSDATA": "",
                    "bili_jct": "",
                    "DedeUserID": "",
                    "buvid3": ""
                },
                "login_method": "qrcode"
            },
            "download": {
                "output_dir": "downloads",
                "quality": "auto",
                "format": "mp4",
                "threads": 4,
                "retry_times": 3,
                "timeout": 30
            },
            "ffmpeg": {
                "path": "auto",
                "auto_merge": true,
                "delete_temp_files": true
            },
            "network": {
                "proxy": "",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            "debug": {
                "enable_logging": false,
                "log_level": "INFO",
                "save_response": false
            }
        }
        
        self.config = default_config
        return self.save_config()

# 全局配置实例
config_manager = ConfigManager()

def init_config() -> bool:
    """初始化配置"""
    if not os.path.exists(config_manager.config_path):
        print("配置文件不存在，正在创建默认配置文件...")
        print("注意：首次使用请运行 'bili-dl login' 命令登录B站账号")
        return config_manager.create_default_config()
    return config_manager.load_config()

# 配置访问快捷方式
def get_config(key: str, default: Any = None) -> Any:
    return config_manager.get(key, default)

def set_config(key: str, value: Any) -> bool:
    return config_manager.set(key, value)

def get_user_cookies() -> Dict[str, str]:
    return config_manager.get_user_cookies()

def update_user_cookies(cookies: Dict[str, str]) -> bool:
    return config_manager.update_user_cookies(cookies)
