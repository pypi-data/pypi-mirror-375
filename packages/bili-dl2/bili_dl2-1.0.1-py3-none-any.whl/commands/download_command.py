"""
下载命令处理模块
处理视频下载相关的命令行功能
"""

import os
import time
from typing import Optional

from config.config_manager import get_config, set_config
from modules.video_info import get_video_download_info, get_video_download_info_with_fallback
from modules.stream_downloader import download_video_stream
from modules.ffmpeg_integration import merge_video_audio, check_ffmpeg_available
from utils.common_utils import (
    sanitize_filename, 
    parse_bvid, 
    parse_av_id, 
    get_bvid_directory, 
    ensure_directory,
    truncate_title,
    write_json_file
)
from modules.login_manager import init_login

def handle_download_command(args) -> int:
    """处理download子命令"""
    # 验证video_id参数
    if not hasattr(args, 'video_id') or not args.video_id:
        print("错误：必须提供视频ID（BV号或AV号）")
        return 1
    
    # 执行下载
    try:
        success = download_video(
            args.video_id, 
            args.output, 
            args.quality, 
            args.no_merge,
            getattr(args, 'no_login', False)
        )
        
        if success:
            print("下载任务完成！")
            return 0
        else:
            print("下载任务失败！")
            return 1
    except Exception as e:
        print(f"下载命令处理异常: {e}")
        import traceback
        traceback.print_exc()
        return 1

def handle_login(force_login: bool = False) -> bool:
    """处理登录流程"""
    try:
        if force_login:
            print("强制重新登录...")
            # 清除现有Cookie
            set_config('user.cookies', {})
        
        if init_login():
            print("登录状态验证成功")
            return True
        else:
            print("登录失败，请检查网络连接或账号信息")
            return False
            
    except Exception as e:
        print(f"登录过程异常: {e}")
        return False

def download_video(video_id: str, output_dir: Optional[str] = None, 
                  quality: Optional[int] = None, no_merge: bool = False, 
                  ignore_login: bool = False) -> bool:
    """主下载函数"""
    try:
        # 解析视频ID
        bvid = parse_bvid(video_id)
        if not bvid:
            av_id = parse_av_id(video_id)
            if av_id:
                print(f"检测到AV号: {av_id}，请使用BV号进行下载")
            else:
                print("无效的视频ID格式，请提供BV号或AV号")
            return False
        
        print(f"开始处理视频: {bvid}")
        
        # 获取下载配置
        download_config = get_config('download', {})
        output_base_dir = output_dir or download_config.get('output_dir', 'downloads')
        ffmpeg_config = get_config('ffmpeg', {})
        auto_merge = ffmpeg_config.get('auto_merge', True) and not no_merge
        
        # 获取BV号子目录
        output_dir = get_bvid_directory(bvid, output_base_dir)
        ensure_directory(output_dir)
        
        # 获取视频下载信息（支持降级）
        print("获取视频信息...")
        if ignore_login:
            download_info = get_video_download_info_with_fallback(bvid, ignore_login=True)
        else:
            download_info = get_video_download_info(bvid)
        
        title = download_info['title']
        sanitized_title = sanitize_filename(title)
        truncated_title = truncate_title(title)
        best_quality = download_info['best_quality']
        stream_data = download_info['stream_data']
        
        print(f"视频标题: {title}")
        print(f"截断标题: {truncated_title}")
        print(f"最佳可用清晰度: {best_quality}")
        print(f"下载目录: {output_dir}")
        
        # 如果指定了清晰度，使用指定清晰度
        if quality is not None and quality != best_quality:
            print(f"使用指定清晰度: {quality}")
            from modules.video_info import get_video_stream_url, get_video_info
            video_info = get_video_info(bvid)
            stream_data = get_video_stream_url(bvid, video_info['cid'], quality=quality)
            best_quality = quality
        
        # 下载视频流
        print("开始下载视频...")
        downloaded_files = download_video_stream(stream_data, sanitized_title, bvid, output_base_dir)
        
        # 保存视频元数据
        metadata_file = os.path.join(output_dir, "metadata.json")
        metadata = {
            'bvid': bvid,
            'title': title,
            'truncated_title': truncated_title,
            'quality': best_quality,
            'download_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'video_info': download_info['video_info'],
            'files': downloaded_files
        }
        if write_json_file(metadata_file, metadata):
            print(f"视频元数据已保存: {metadata_file}")
        
        # 处理DASH格式视频合并
        if 'dash' in stream_data and auto_merge:
            if check_ffmpeg_available():
                print("检测到DASH格式视频，开始合并音视频...")
                video_path = downloaded_files.get('video')
                audio_path = downloaded_files.get('audio')
                final_output = os.path.join(output_dir, f"{sanitized_title}.mp4")
                
                success, message = merge_video_audio(video_path, audio_path, final_output)
                if success:
                    print(f"视频合并成功: {final_output}")
                    return True
                else:
                    print(f"视频合并失败: {message}")
                    print("请手动使用ffmpeg合并文件:")
                    print(f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c copy \"{final_output}\"")
                    return False
            else:
                print("ffmpeg不可用，无法自动合并DASH视频")
                print("请手动使用ffmpeg合并文件:")
                video_path = downloaded_files.get('video')
                audio_path = downloaded_files.get('audio')
                final_output = os.path.join(output_dir, f"{sanitized_title}.mp4")
                print(f"ffmpeg -i \"{video_path}\" -i \"{audio_path}\" -c copy \"{final_output}\"")
                return True
        
        # MP4格式直接下载完成
        elif 'durl' in stream_data:
            print(f"视频下载完成: {downloaded_files.get('video')}")
            return True
        
        else:
            print("未知的视频格式")
            return False
            
    except KeyboardInterrupt:
        print("\n用户中断下载")
        return False
    except Exception as e:
        print(f"下载过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False
