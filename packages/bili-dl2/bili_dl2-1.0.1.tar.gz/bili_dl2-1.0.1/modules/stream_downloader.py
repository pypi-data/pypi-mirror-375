import requests
import os
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.config_manager import get_config
from modules.login_manager import get_session

class StreamDownloader:
    def __init__(self):
        self.session = get_session()
        self.logger = logging.getLogger(__name__)
        self.download_config = get_config('download', {})
        
    def download_file(self, url: str, filename: str, 
                     chunk_size: int = 8192, 
                     progress_callback: Optional[Callable] = None) -> bool:
        """下载单个文件"""
        try:
            # 检查文件是否已存在（支持断点续传）
            file_size = 0
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                self.logger.info(f"文件已存在，尝试断点续传: {filename} ({file_size} bytes)")
            
            headers = {}
            if file_size > 0:
                headers['Range'] = f'bytes={file_size}-'
            
            response = self.session.get(url, headers=headers, stream=True, timeout=self.download_config.get('timeout', 30))
            
            if response.status_code in [200, 206]:  # 200 OK or 206 Partial Content
                total_size = int(response.headers.get('content-length', 0)) + file_size
                downloaded_size = file_size
                
                mode = 'ab' if file_size > 0 else 'wb'
                with open(filename, mode) as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # 调用进度回调
                            if progress_callback:
                                progress_callback(downloaded_size, total_size, filename)
                
                self.logger.info(f"下载完成: {filename}")
                return True
            else:
                self.logger.error(f"下载失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"下载文件异常 {filename}: {e}")
            return False
    
    def download_with_retry(self, url: str, filename: str, 
                           max_retries: int = 3,
                           progress_callback: Optional[Callable] = None) -> bool:
        """带重试机制的下载"""
        retries = 0
        while retries < max_retries:
            try:
                if self.download_file(url, filename, progress_callback=progress_callback):
                    return True
            except Exception as e:
                self.logger.warning(f"下载尝试 {retries + 1} 失败: {e}")
            
            retries += 1
            if retries < max_retries:
                wait_time = 2 ** retries  # 指数退避
                self.logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        self.logger.error(f"下载失败，已达到最大重试次数: {max_retries}")
        return False
    
    def download_multiple_files(self, file_list: list, max_workers: int = 4) -> Dict[str, bool]:
        """多线程下载多个文件"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有下载任务
            future_to_file = {
                executor.submit(
                    self.download_with_retry, 
                    file_info['url'], 
                    file_info['filename'],
                    self.download_config.get('retry_times', 3)
                ): file_info['filename']
                for file_info in file_list
            }
            
            # 收集结果
            for future in as_completed(future_to_file):
                filename = future_to_file[future]
                try:
                    results[filename] = future.result()
                except Exception as e:
                    self.logger.error(f"下载任务异常 {filename}: {e}")
                    results[filename] = False
        
        return results
    
    def download_video_stream(self, stream_data: Dict[str, Any], title: str, 
                            bvid: str, output_base_dir: str = 'download') -> Dict[str, str]:
        """下载视频流（支持DASH和MP4格式）"""
        try:
            # 创建BV号子目录
            from utils.common_utils import truncate_title, get_bvid_directory, ensure_directory
            output_dir = get_bvid_directory(bvid, output_base_dir)
            ensure_directory(output_dir)
            
            # 截断标题
            truncated_title = truncate_title(title)
            downloaded_files = {}
            
            if 'dash' in stream_data:
                # DASH格式：分别下载视频和音频
                dash_data = stream_data['dash']
                
                # 下载视频流
                video_url = dash_data['video'][0]['baseUrl']
                video_filename = os.path.join(output_dir, f"{truncated_title}_video.m4s")
                downloaded_files['video'] = video_filename
                
                print(f"下载视频流: {video_filename}")
                if not self.download_with_retry(video_url, video_filename):
                    raise Exception("视频流下载失败")
                
                # 下载音频流
                audio_url = dash_data['audio'][0]['baseUrl']
                audio_filename = os.path.join(output_dir, f"{truncated_title}_audio.m4s")
                downloaded_files['audio'] = audio_filename
                
                print(f"下载音频流: {audio_filename}")
                if not self.download_with_retry(audio_url, audio_filename):
                    raise Exception("音频流下载失败")
                    
            elif 'durl' in stream_data:
                # MP4格式：直接下载完整文件
                durl = stream_data['durl'][0]
                video_url = durl['url']
                final_filename = os.path.join(output_dir, f"{truncated_title}.mp4")
                downloaded_files['video'] = final_filename
                
                print(f"下载MP4视频: {final_filename}")
                if not self.download_with_retry(video_url, final_filename):
                    raise Exception("MP4视频下载失败")
            
            else:
                raise Exception("未知的视频流格式")
            
            return downloaded_files
            
        except Exception as e:
            self.logger.error(f"下载视频流失败: {e}")
            # 清理可能已下载的部分文件
            for filename in downloaded_files.values():
                if os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except:
                        pass
            raise
    
    def create_progress_callback(self, total_files: int = 1) -> Callable:
        """创建进度回调函数"""
        lock = threading.Lock()
        completed_files = 0
        
        def progress_callback(downloaded: int, total: int, filename: str):
            nonlocal completed_files
            with lock:
                if total > 0:
                    percentage = (downloaded / total) * 100
                    print(f"\r{filename}: {percentage:.1f}% ({downloaded}/{total} bytes)", end='')
                    
                    if downloaded >= total:
                        completed_files += 1
                        print(f"\n文件下载完成 ({completed_files}/{total_files})")
        
        return progress_callback

# 全局下载器实例
stream_downloader = StreamDownloader()

def download_file(url: str, filename: str, progress_callback: Optional[Callable] = None) -> bool:
    """下载单个文件"""
    return stream_downloader.download_file(url, filename, progress_callback=progress_callback)

def download_with_retry(url: str, filename: str, max_retries: int = 3, 
                       progress_callback: Optional[Callable] = None) -> bool:
    """带重试机制的下载"""
    return stream_downloader.download_with_retry(url, filename, max_retries, progress_callback)

def download_video_stream(stream_data: Dict[str, Any], title: str, bvid: str,
                         output_base_dir: str = 'download') -> Dict[str, str]:
    """下载视频流"""
    return stream_downloader.download_video_stream(stream_data, title, bvid, output_base_dir)

def create_progress_callback(total_files: int = 1) -> Callable:
    """创建进度回调函数"""
    return stream_downloader.create_progress_callback(total_files)
