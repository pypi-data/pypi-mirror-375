import os
import subprocess
import logging
import shutil
from typing import Dict, Optional, Tuple
from config.config_manager import get_config

class FFmpegIntegration:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ffmpeg_config = get_config('ffmpeg', {})
        self.ffmpeg_path = self._find_ffmpeg()
        
    def _find_ffmpeg(self) -> Optional[str]:
        """查找ffmpeg可执行文件路径"""
        # 首先检查配置中的路径
        config_path = self.ffmpeg_config.get('path', 'auto')
        if config_path != 'auto' and os.path.exists(config_path):
            return config_path
        
        # 检查系统PATH中的ffmpeg
        ffmpeg_executable = 'ffmpeg.exe' if os.name == 'nt' else 'ffmpeg'
        ffmpeg_path = shutil.which(ffmpeg_executable)
        
        if ffmpeg_path:
            return ffmpeg_path
        
        # 检查常见安装路径（Windows）
        if os.name == 'nt':
            common_paths = [
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'D:\Program Files\ffmpeg\bin\ffmpeg.exe',
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        self.logger.warning("未找到ffmpeg，请安装ffmpeg并添加到PATH环境变量")
        return None
    
    def check_ffmpeg_available(self) -> bool:
        """检查ffmpeg是否可用"""
        if not self.ffmpeg_path:
            return False
        
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def merge_video_audio(self, video_path: str, audio_path: str, output_path: str) -> Tuple[bool, str]:
        """合并视频和音频文件"""
        if not self.check_ffmpeg_available():
            return False, "ffmpeg不可用"
        
        if not os.path.exists(video_path) or not os.path.exists(audio_path):
            return False, "输入文件不存在"
        
        try:
            # 构建ffmpeg命令
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,    # 输入视频文件
                '-i', audio_path,    # 输入音频文件
                '-c', 'copy',        # 直接复制流，不重新编码
                '-y',                # 覆盖输出文件
                output_path          # 输出文件
            ]
            
            self.logger.info(f"执行ffmpeg命令: {' '.join(cmd)}")
            
            # 执行ffmpeg命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 实时输出进度信息
            while True:
                output = process.stderr.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    try:
                        # 解码输出，尝试utf-8，如果失败则使用系统默认编码
                        output_str = output.decode('utf-8', errors='ignore')
                        # 解析进度信息（如果有）
                        if 'time=' in output_str:
                            time_info = output_str.split('time=')[1].split(' ')[0]
                            print(f"\r合并进度: {time_info}", end='')
                    except UnicodeDecodeError:
                        # 如果utf-8解码失败，尝试其他编码
                        try:
                            output_str = output.decode('gbk', errors='ignore')
                            if 'time=' in output_str:
                                time_info = output_str.split('time=')[1].split(' ')[0]
                                print(f"\r合并进度: {time_info}", end='')
                        except:
                            pass
            
            returncode = process.poll()
            
            if returncode == 0:
                print("\n音视频合并完成！")
                
                # 检查是否需要删除临时文件
                if self.ffmpeg_config.get('delete_temp_files', True):
                    try:
                        os.remove(video_path)
                        os.remove(audio_path)
                        self.logger.info("已删除临时文件")
                    except Exception as e:
                        self.logger.warning(f"删除临时文件失败: {e}")
                
                return True, "合并成功"
            else:
                try:
                    error_output = process.stderr.read().decode('utf-8', errors='ignore')
                except:
                    error_output = process.stderr.read().decode('gbk', errors='ignore')
                return False, f"ffmpeg执行失败: {error_output}"
                
        except Exception as e:
            return False, f"合并过程异常: {str(e)}"
    
    def convert_to_mp4(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """转换视频格式到MP4"""
        if not self.check_ffmpeg_available():
            return False, "ffmpeg不可用"
        
        if not os.path.exists(input_path):
            return False, "输入文件不存在"
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c', 'copy',  # 直接复制，不重新编码
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                return True, "转换成功"
            else:
                return False, f"转换失败: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "转换超时"
        except Exception as e:
            return False, f"转换过程异常: {str(e)}"
    
    def get_video_info(self, video_path: str) -> Optional[Dict]:
        """获取视频文件信息"""
        if not self.check_ffmpeg_available():
            return None
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-hide_banner'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 解析ffmpeg输出获取视频信息
            info = {}
            stderr = result.stderr
            
            # 解析时长
            if 'Duration:' in stderr:
                duration_line = stderr.split('Duration:')[1].split(',')[0].strip()
                info['duration'] = duration_line
            
            # 解析视频流信息
            if 'Video:' in stderr:
                video_line = stderr.split('Video:')[1].split('\n')[0].strip()
                info['video'] = video_line
            
            # 解析音频流信息
            if 'Audio:' in stderr:
                audio_line = stderr.split('Audio:')[1].split('\n')[0].strip()
                info['audio'] = audio_line
            
            return info if info else None
            
        except Exception as e:
            self.logger.error(f"获取视频信息失败: {e}")
            return None

# 全局ffmpeg集成实例
ffmpeg_integration = FFmpegIntegration()

def check_ffmpeg_available() -> bool:
    """检查ffmpeg是否可用"""
    return ffmpeg_integration.check_ffmpeg_available()

def merge_video_audio(video_path: str, audio_path: str, output_path: str) -> Tuple[bool, str]:
    """合并视频和音频文件"""
    return ffmpeg_integration.merge_video_audio(video_path, audio_path, output_path)

def convert_to_mp4(input_path: str, output_path: str) -> Tuple[bool, str]:
    """转换视频格式到MP4"""
    return ffmpeg_integration.convert_to_mp4(input_path, output_path)

def get_video_info(video_path: str) -> Optional[Dict]:
    """获取视频文件信息"""
    return ffmpeg_integration.get_video_info(video_path)
