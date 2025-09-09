import os
import re
import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """设置日志配置"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 基础配置
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件日志（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)

def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """清理文件名，移除非法字符"""
    # 移除非法字符
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除连续的下划线
    sanitized = re.sub(r'_+', '_', sanitized)
    # 移除首尾的下划线和空格
    sanitized = sanitized.strip(' _')
    # 限制长度
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip(' _')
    # 确保不为空
    if not sanitized:
        sanitized = "unnamed"
    return sanitized

def truncate_title(title: str, max_words: int = 8) -> str:
    """截断标题，保留前N个字，其余用省略号"""
    if len(title) <= max_words:
        return title
    return title[:max_words] + "..."

def get_bvid_directory(bvid: str, base_dir: str = "download") -> str:
    """获取BV号对应的下载目录"""
    return os.path.join(base_dir, bvid)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def format_duration(seconds: int) -> str:
    """格式化时间持续时间"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def ensure_directory(directory: str) -> bool:
    """确保目录存在"""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"创建目录失败 {directory}: {e}")
        return False

def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"读取JSON文件失败 {file_path}: {e}")
        return None

def write_json_file(file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
    """写入JSON文件"""
    try:
        ensure_directory(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"写入JSON文件失败 {file_path}: {e}")
        return False

def parse_bvid(input_str: str) -> Optional[str]:
    """解析BV号"""
    # 匹配BV号格式
    bv_match = re.search(r'(BV[0-9A-Za-z]{10})', input_str)
    if bv_match:
        return bv_match.group(1)
    
    # 匹配URL中的BV号
    url_match = re.search(r'bilibili\.com/video/(BV[0-9A-Za-z]{10})', input_str)
    if url_match:
        return url_match.group(1)
    
    return None

def parse_av_id(input_str: str) -> Optional[str]:
    """解析AV号"""
    # 匹配AV号格式
    av_match = re.search(r'(av\d+)', input_str, re.IGNORECASE)
    if av_match:
        return av_match.group(1).lower()
    
    # 匹配URL中的AV号
    url_match = re.search(r'bilibili\.com/video/(av\d+)', input_str, re.IGNORECASE)
    if url_match:
        return url_match.group(1).lower()
    
    return None

def is_valid_url(url: str) -> bool:
    """检查是否为有效的URL"""
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(([A-Z0-9][A-Z0-9_-]*(?:\.[A-Z0-9][A-Z0-9_-]*)+)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def human_readable_speed(speed_bytes_per_sec: float) -> str:
    """格式化下载速度"""
    if speed_bytes_per_sec <= 0:
        return "0 B/s"
    
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    speed = speed_bytes_per_sec
    unit_index = 0
    
    while speed >= 1024 and unit_index < len(units) - 1:
        speed /= 1024
        unit_index += 1
    
    return f"{speed:.2f} {units[unit_index]}"

def progress_bar(current: int, total: int, length: int = 50) -> str:
    """生成进度条字符串"""
    if total <= 0:
        return "[{}] 0%".format(" " * length)
    
    percent = current / total
    filled_length = int(length * percent)
    bar = "█" * filled_length + " " * (length - filled_length)
    return "[{}] {:.1f}%".format(bar, percent * 100)

def get_file_extension(url: str) -> str:
    """从URL获取文件扩展名"""
    # 移除查询参数
    clean_url = url.split('?')[0]
    # 获取扩展名
    ext = os.path.splitext(clean_url)[1].lower()
    return ext if ext else '.bin'

def chunked_download_info(total_size: int, chunk_size: int = 1024 * 1024) -> List[Dict[str, int]]:
    """生成分块下载信息"""
    chunks = []
    start = 0
    
    while start < total_size:
        end = min(start + chunk_size - 1, total_size - 1)
        chunks.append({'start': start, 'end': end, 'size': end - start + 1})
        start = end + 1
    
    return chunks

def validate_cookies(cookies: Dict[str, str]) -> bool:
    """验证Cookie是否有效"""
    required_cookies = ['SESSDATA', 'bili_jct', 'DedeUserID']
    return all(cookie in cookies and cookies[cookie] for cookie in required_cookies)

def format_timestamp(timestamp: int) -> str:
    """格式化时间戳"""
    from datetime import datetime
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
