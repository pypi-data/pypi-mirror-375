import requests
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

from config.config_manager import get_config
from modules.login_manager import get_session

class VideoInfoManager:
    def __init__(self):
        self.session = get_session()
        self.logger = logging.getLogger(__name__)
        self.wbi_salt = ""  # WBI签名盐值
        
    def get_video_info(self, bvid: str) -> Dict[str, Any]:
        """获取视频基本信息"""
        try:
            url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data['data']
                else:
                    raise Exception(f"获取视频信息失败: {data.get('message', '未知错误')}")
            else:
                raise Exception(f"HTTP请求失败: {response.status_code}")
        except Exception as e:
            self.logger.error(f"获取视频信息异常: {e}")
            raise
    
    def get_wbi_salt(self) -> Optional[str]:
        """获取WBI签名盐值"""
        try:
            url = "https://api.bilibili.com/x/web-interface/nav"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    wbi_img = data['data']['wbi_img']
                    # 从URL中提取盐值
                    if 'key1' in wbi_img['img_url'] and 'key2' in wbi_img['sub_url']:
                        key1 = wbi_img['img_url'].split('key1=')[1].split('&')[0]
                        key2 = wbi_img['sub_url'].split('key2=')[1].split('&')[0]
                        return key1 + key2
            return None
        except Exception as e:
            self.logger.error(f"获取WBI盐值失败: {e}")
            return None
    
    def wbi_sign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """WBI签名算法"""
        if not self.wbi_salt:
            self.wbi_salt = self.get_wbi_salt() or ""
        
        # 添加时间戳
        params['wts'] = int(time.time())
        
        # 参数排序并过滤
        filtered_params = {k: v for k, v in params.items() if v is not None and v != ""}
        sorted_params = dict(sorted(filtered_params.items()))
        
        # 生成签名
        query_string = urlencode(sorted_params)
        sign_string = query_string + self.wbi_salt
        w_rid = hashlib.md5(sign_string.encode()).hexdigest()
        
        # 添加签名到参数
        signed_params = sorted_params.copy()
        signed_params['w_rid'] = w_rid
        return signed_params
    
    def get_video_stream_url(self, bvid: str, cid: int, quality: int = 80, fnval: int = 4048) -> Dict[str, Any]:
        """
        获取视频流地址
        quality: 清晰度代码
        fnval: 视频格式标识 (4048 = 所有DASH格式)
        """
        try:
            # 构建参数
            params = {
                'bvid': bvid,
                'cid': cid,
                'qn': quality,
                'fnval': fnval,
                'fnver': 0,
                'fourk': 1,
                'otype': 'json',
                'platform': 'pc'
            }
            
            # WBI签名
            signed_params = self.wbi_sign(params)
            
            url = "https://api.bilibili.com/x/player/wbi/playurl"
            response = self.session.get(url, params=signed_params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    return data['data']
                else:
                    raise Exception(f"获取视频流失败: {data.get('message', '未知错误')}")
            else:
                raise Exception(f"HTTP请求失败: {response.status_code}")
        except Exception as e:
            self.logger.error(f"获取视频流异常: {e}")
            raise
    
    def get_highest_quality_available(self, stream_data: Dict[str, Any]) -> int:
        """根据账号权限获取可用的最高清晰度"""
        try:
            if 'accept_quality' in stream_data:
                available_qualities = stream_data['accept_quality']
                
                # 清晰度优先级（从高到低）
                quality_priority = [
                    127,  # 8K超高清
                    126,  # 杜比视界
                    125,  # HDR真彩色
                    120,  # 4K超清
                    116,  # 1080P60高帧率
                    112,  # 1080P+高码率
                    100,  # 智能修复
                    80,   # 1080P高清
                    74,   # 720P60高帧率
                    64,   # 720P高清
                    32,   # 480P清晰
                    16,   # 360P流畅
                    6     # 240P极速
                ]
                
                # 找到账号权限内可用的最高清晰度
                for quality in quality_priority:
                    if quality in available_qualities:
                        return quality
                
                # 如果没有找到优先级的清晰度，返回列表中的最高清晰度
                return max(available_qualities) if available_qualities else 64
            
            return 64  # 默认返回720P
        except Exception as e:
            self.logger.error(f"获取最高清晰度失败: {e}")
            return 64
    
    def get_video_quality_list(self, bvid: str, cid: int) -> List[Dict[str, Any]]:
        """获取视频可用的清晰度列表"""
        try:
            stream_data = self.get_video_stream_url(bvid, cid)
            
            if 'accept_description' in stream_data and 'accept_quality' in stream_data:
                qualities = []
                for desc, quality in zip(stream_data['accept_description'], stream_data['accept_quality']):
                    qualities.append({
                        'quality': quality,
                        'description': desc,
                        'selected': False
                    })
                return qualities
            return []
        except Exception as e:
            self.logger.error(f"获取清晰度列表失败: {e}")
            return []
    
    def get_video_download_info(self, bvid: str) -> Dict[str, Any]:
        """获取视频下载信息（整合视频信息和流信息）"""
        try:
            # 获取视频基本信息
            video_info = self.get_video_info(bvid)
            title = video_info['title']
            cid = video_info['cid']
            
            # 获取流信息
            stream_data = self.get_video_stream_url(bvid, cid)
            
            # 获取最高清晰度
            best_quality = self.get_highest_quality_available(stream_data)
            
            # 使用最高清晰度重新获取流信息
            if best_quality != 80:
                stream_data = self.get_video_stream_url(bvid, cid, quality=best_quality)
            
            return {
                'video_info': video_info,
                'stream_data': stream_data,
                'best_quality': best_quality,
                'title': title,
                'cid': cid,
                'bvid': bvid
            }
        except Exception as e:
            self.logger.error(f"获取视频下载信息失败: {e}")
            raise

    def get_video_download_info_with_fallback(self, bvid: str, ignore_login: bool = False) -> Dict[str, Any]:
        """
        获取视频下载信息，支持登录状态降级
        
        Args:
            bvid: 视频BV号
            ignore_login: 是否忽略登录状态，强制使用访客模式
            
        Returns:
            视频下载信息，包含降级后的清晰度信息
        """
        try:
            # 获取视频基本信息（不需要登录）
            video_info = self.get_video_info(bvid)
            title = video_info['title']
            cid = video_info['cid']
            
            # 清晰度降级策略（从高到低）
            fallback_qualities = [
                127,  # 8K超高清
                126,  # 杜比视界
                125,  # HDR真彩色
                120,  # 4K超清
                116,  # 1080P60高帧率
                112,  # 1080P+高码率
                100,  # 智能修复
                80,   # 1080P高清
                74,   # 720P60高帧率
                64,   # 720P高清
                32,   # 480P清晰
                16,   # 360P流畅
                6     # 240P极速
            ]
            
            last_exception = None
            used_quality = None
            
            # 尝试从最高清晰度开始降级
            for quality in fallback_qualities:
                try:
                    # 获取流信息
                    stream_data = self.get_video_stream_url(bvid, cid, quality=quality)
                    
                    # 检查是否成功获取到流信息
                    if stream_data and 'dash' in stream_data or 'durl' in stream_data:
                        used_quality = quality
                        break
                        
                except Exception as e:
                    last_exception = e
                    self.logger.debug(f"清晰度 {quality} 获取失败: {e}")
                    continue
            
            # 如果所有清晰度都失败，抛出最后一个异常
            if used_quality is None and last_exception:
                raise last_exception
            
            # 如果使用了降级后的清晰度，重新获取流信息确保一致性
            if used_quality != 80:
                stream_data = self.get_video_stream_url(bvid, cid, quality=used_quality)
            
            return {
                'video_info': video_info,
                'stream_data': stream_data,
                'best_quality': used_quality or 64,  # 默认720P
                'title': title,
                'cid': cid,
                'bvid': bvid,
                'is_fallback': used_quality != self.get_highest_quality_available(stream_data) if used_quality else False
            }
            
        except Exception as e:
            self.logger.error(f"获取视频下载信息（降级模式）失败: {e}")
            
            # 如果忽略登录状态，尝试使用最低清晰度
            if ignore_login:
                try:
                    # 使用最低清晰度（360P）作为最后手段
                    stream_data = self.get_video_stream_url(bvid, cid, quality=16)
                    return {
                        'video_info': video_info,
                        'stream_data': stream_data,
                        'best_quality': 16,
                        'title': title,
                        'cid': cid,
                        'bvid': bvid,
                        'is_fallback': True
                    }
                except Exception:
                    # 如果连最低清晰度都失败，抛出原始异常
                    raise e
            else:
                raise

# 全局视频信息管理器实例
video_info_manager = VideoInfoManager()

def get_video_info(bvid: str) -> Dict[str, Any]:
    """获取视频信息"""
    return video_info_manager.get_video_info(bvid)

def get_video_stream_url(bvid: str, cid: int, quality: int = 80, fnval: int = 4048) -> Dict[str, Any]:
    """获取视频流地址"""
    return video_info_manager.get_video_stream_url(bvid, cid, quality, fnval)

def get_highest_quality_available(stream_data: Dict[str, Any]) -> int:
    """获取最高可用清晰度"""
    return video_info_manager.get_highest_quality_available(stream_data)

def get_video_download_info(bvid: str) -> Dict[str, Any]:
    """获取视频下载信息"""
    return video_info_manager.get_video_download_info(bvid)

def get_video_download_info_with_fallback(bvid: str, ignore_login: bool = False) -> Dict[str, Any]:
    """获取视频下载信息，支持登录状态降级"""
    return video_info_manager.get_video_download_info_with_fallback(bvid, ignore_login)
