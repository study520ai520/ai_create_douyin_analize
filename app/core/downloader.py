"""
抖音视频下载器核心模块
"""
import os
import time
import json
import re
import random
import pickle
import base64
import urllib.parse
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 常用User-Agent列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

class DouyinDownloader:
    """抖音视频下载器"""

    def __init__(self, use_proxy: bool = False, proxy_url: str = None):
        """初始化下载器
        
        Args:
            use_proxy: 是否使用代理
            proxy_url: 代理服务器地址，如 http://127.0.0.1:7890
        """
        # 随机选择一个User-Agent
        self.user_agent = random.choice(USER_AGENTS)
        
        # 设置会话
        self.session = requests.Session()
        
        # 设置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置基本请求头
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # 设置代理
        self.proxies = None
        if use_proxy:
            if proxy_url:
                self.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                # 使用默认代理
                self.proxies = {
                    'http': 'http://127.0.0.1:7890',
                    'https': 'http://127.0.0.1:7890'
                }
            self.session.proxies = self.proxies
            logger.info(f"已设置代理: {self.proxies}")
            
        # 设置cookies文件路径
        self.cookies_file = Path("data/cookies.pkl")
            
        # 加载cookies
        self._load_cookies()

    def _create_session(self) -> requests.Session:
        """创建请求会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,  # 最大重试次数
            backoff_factor=1,  # 重试间隔
            status_forcelist=[429, 500, 502, 503, 504]  # 需要重试的HTTP状态码
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置基础请求头
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.douyin.com/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1'
        })
        
        return session

    def _load_cookies(self):
        """加载Cookies"""
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, 'rb') as f:
                    self.session.cookies.update(pickle.load(f))
                logger.info("已加载保存的Cookies")
            except Exception as e:
                logger.error(f"加载Cookies失败: {str(e)}")

    def _save_cookies(self):
        """保存Cookies"""
        try:
            self.cookies_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(self.session.cookies, f)
            logger.info("已保存Cookies")
        except Exception as e:
            logger.error(f"保存Cookies失败: {str(e)}")

    def _update_headers(self):
        """更新请求头"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS)
        })

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """发送HTTP请求
        
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 其他请求参数
            
        Returns:
            Response对象或None
        """
        try:
            # 更新User-Agent
            self.session.headers.update({
                'User-Agent': random.choice(USER_AGENTS)
            })
            
            # 发送请求
            response = self.session.request(method, url, **kwargs)
            
            # 保存Cookies
            self._save_cookies()
            
            return response
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return None

    def parse_url(self, url: str) -> Optional[str]:
        """解析抖音URL，支持短链接"""
        try:
            if 'v.douyin.com' in url:
                response = self._make_request('HEAD', url, allow_redirects=True)
                if not response:
                    return None
                url = response.url
            
            # 提取用户ID
            match = re.search(r'user/([^/?]+)', url)
            if match:
                user_id = match.group(1)
                return f"https://www.douyin.com/user/{user_id}"
            return None
        except Exception as e:
            logger.error(f"解析URL失败: {str(e)}")
            return None

    def _init_user_session(self, user_url: str) -> bool:
        """初始化用户会话，获取必要的cookies和参数
        
        Args:
            user_url: 用户主页URL
            
        Returns:
            bool: 是否初始化成功
        """
        try:
            # 访问主页获取初始cookies
            response = self._make_request('GET', 'https://www.douyin.com/')
            if not response or response.status_code != 200:
                logger.error("访问主页失败")
                return False
                
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 访问用户页面
            response = self._make_request('GET', user_url)
            if not response or response.status_code != 200:
                logger.error("访问用户页面失败")
                return False
            
            # 解析ttwid
            ttwid = response.cookies.get('ttwid')
            if not ttwid:
                logger.warning("未获取到ttwid")
            
            # 解析msToken
            ms_token = response.cookies.get('msToken')
            if not ms_token:
                logger.warning("未获取到msToken")
            
            # 保存cookies
            self._save_cookies()
            
            return True
            
        except Exception as e:
            logger.error(f"初始化用户会话失败: {str(e)}")
            return False

    def get_user_info(self, url: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            # 初始化用户会话
            if not self._init_user_session(url):
                logger.error("初始化用户会话失败")
                return None
            
            # 获取用户页面
            response = self._make_request('GET', url)
            if not response or response.status_code != 200:
                logger.error(f"获取用户页面失败: {response.status_code if response else 'No response'}")
                return None

            # 保存响应内容用于调试
            debug_file = Path("data/logs/debug_response.html")
            debug_file.write_text(response.text, encoding='utf-8')
            logger.info(f"已保存调试响应到: {debug_file}")

            # 解析页面
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 尝试不同的数据提取方法
            user_info = None
            
            # 方法1: 查找RENDER_DATA脚本
            render_data = soup.find('script', id='RENDER_DATA')
            if render_data:
                try:
                    # RENDER_DATA可能是base64编码的
                    data_str = render_data.string
                    if data_str:
                        # 尝试base64解码
                        try:
                            data_str = base64.b64decode(data_str).decode('utf-8')
                        except:
                            pass
                        data = json.loads(data_str)
                        logger.debug(f"RENDER_DATA解析结果: {data}")
                        
                        # 遍历所有可能包含用户信息的字段
                        for key, value in data.items():
                            if isinstance(value, dict):
                                user_data = value.get('user') or value.get('userInfo')
                                if user_data:
                                    user_info = {
                                        'user_id': user_data.get('uid') or user_data.get('id'),
                                        'nickname': user_data.get('nickname'),
                                        'signature': user_data.get('signature'),
                                        'following_count': user_data.get('following_count'),
                                        'follower_count': user_data.get('follower_count'),
                                        'liked_count': user_data.get('total_favorited')
                                    }
                                    break
                except Exception as e:
                    logger.error(f"解析RENDER_DATA失败: {str(e)}")

            # 方法2: 查找用户信息相关的其他脚本
            if not user_info:
                for script in soup.find_all('script'):
                    if script.string and 'userInfo' in script.string:
                        try:
                            # 使用正则提取JSON数据
                            match = re.search(r'window\._SSR_HYDRATED_DATA\s*=\s*({.+?})</script>', script.string)
                            if match:
                                data = json.loads(match.group(1))
                                user_data = data.get('userInfo', {})
                                user_info = {
                                    'user_id': user_data.get('uid') or user_data.get('id'),
                                    'nickname': user_data.get('nickname'),
                                    'signature': user_data.get('signature'),
                                    'following_count': user_data.get('following_count'),
                                    'follower_count': user_data.get('follower_count'),
                                    'liked_count': user_data.get('total_favorited')
                                }
                                break
                        except Exception as e:
                            logger.error(f"解析脚本数据失败: {str(e)}")
                            continue

            # 方法3: 从URL中提取用户ID
            if not user_info:
                user_id = re.search(r'user/([^/?]+)', url)
                if user_id:
                    user_info = {
                        'user_id': user_id.group(1),
                        'nickname': 'Unknown',
                        'signature': '',
                        'following_count': 0,
                        'follower_count': 0,
                        'liked_count': 0
                    }
                    logger.warning("仅从URL提取到用户ID，其他信息未获取")

            if user_info:
                logger.info(f"成功获取用户信息: {user_info}")
                return user_info
            else:
                logger.error("无法从页面提取用户信息")
                return None

        except Exception as e:
            logger.exception(f"获取用户信息失败: {str(e)}")
            return None

    def get_video_list(self, user_id: str, max_cursor: int = 0) -> Tuple[List[Dict], int]:
        """获取视频列表"""
        try:
            # 使用新的API端点
            api_url = f"https://www.douyin.com/aweme/v1/web/aweme/post/"
            
            # 获取API参数
            params = self._get_api_params()
            params.update({
                'sec_user_id': user_id,
                'max_cursor': max_cursor
            })
            
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': f'https://www.douyin.com/user/{user_id}',
                'User-Agent': self.user_agent,
                'Origin': 'https://www.douyin.com',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 保存请求信息用于调试
            logger.debug(f"请求视频列表: {api_url}")
            logger.debug(f"请求参数: {params}")
            
            response = self._make_request('GET', api_url, params=params, headers=headers)
            
            if not response or response.status_code != 200:
                logger.error(f"获取视频列表失败: {response.status_code if response else 'No response'}")
                # 保存响应内容用于调试
                if response:
                    debug_file = Path("data/logs/video_list_response.json")
                    debug_file.write_text(response.text, encoding='utf-8')
                    logger.info(f"已保存视频列表响应到: {debug_file}")
                return [], 0

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"解析视频列表JSON失败: {str(e)}")
                debug_file = Path("data/logs/video_list_response.json")
                debug_file.write_text(response.text, encoding='utf-8')
                logger.info(f"已保存视频列表响应到: {debug_file}")
                return [], 0

            videos = []
            for item in data.get('aweme_list', []):
                video_info = {
                    'video_id': item.get('aweme_id'),
                    'title': item.get('desc'),
                    'cover': item.get('video', {}).get('cover', {}).get('url_list', [None])[0],
                    'play_url': item.get('video', {}).get('play_addr', {}).get('url_list', [None])[0],
                    'create_time': item.get('create_time'),
                    'statistics': {
                        'comment_count': item.get('statistics', {}).get('comment_count', 0),
                        'digg_count': item.get('statistics', {}).get('digg_count', 0),
                        'share_count': item.get('statistics', {}).get('share_count', 0)
                    }
                }
                videos.append(video_info)

            has_more = data.get('has_more', False)
            next_cursor = data.get('max_cursor', 0) if has_more else 0
            
            logger.info(f"成功获取视频列表: {len(videos)} 个视频")
            return videos, next_cursor
            
        except Exception as e:
            logger.exception(f"获取视频列表失败: {str(e)}")
            return [], 0

    def download_video(self, video_url: str, save_path: str) -> bool:
        """下载视频
        
        Args:
            video_url: 视频URL
            save_path: 保存路径
            
        Returns:
            bool: 是否下载成功
        """
        try:
            # 创建保存目录
            save_dir = os.path.dirname(save_path)
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
            
            # 设置视频下载请求头
            headers = {
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Accept-Encoding': 'identity;q=1, *;q=0',
                'Range': 'bytes=0-',
                'Referer': 'https://www.douyin.com/',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 获取视频内容
            response = self._make_request('GET', video_url, stream=True, headers=headers)
            if not response or response.status_code not in [200, 206]:
                logger.error(f"下载视频失败: {response.status_code if response else 'No response'}")
                return False

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1MB
            downloaded_size = 0
            
            # 保存视频
            with open(save_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded_size += len(data)
                    f.write(data)
                    # 打印下载进度
                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        logger.debug(f"下载进度: {progress:.1f}%")

            # 验证文件大小
            if total_size > 0 and os.path.getsize(save_path) != total_size:
                logger.error(f"文件大小不匹配: 期望 {total_size}，实际 {os.path.getsize(save_path)}")
                return False

            logger.info(f"视频下载完成: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    logger.info(f"已删除失败的下载文件: {save_path}")
                except:
                    pass
            return False

    def download_all_videos(self, user_url: str) -> List[Dict]:
        """下载用户所有视频
        
        Args:
            user_url: 用户主页URL
            
        Returns:
            List[Dict]: 下载结果列表，每个字典包含:
                - video_id: 视频ID
                - title: 视频标题
                - status: 下载状态 (success/failed/skipped)
                - error: 错误信息 (如果失败)
                - path: 保存路径 (如果成功)
        """
        try:
            # 解析用户URL
            user_url = self.parse_url(user_url)
            if not user_url:
                raise Exception("无效的用户URL")
            
            # 获取用户信息
            user_info = self.get_user_info(user_url)
            if not user_info:
                raise Exception("获取用户信息失败")
            
            # 创建下载目录
            download_dir = Path("data/downloads") / user_info['nickname']
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取所有视频
            results = []
            has_more = True
            max_cursor = 0
            
            while has_more:
                videos, next_cursor = self.get_video_list(user_info['user_id'], max_cursor)
                
                for video in videos:
                    result = {
                        'video_id': video['video_id'],
                        'title': video['title'] or f"video_{video['video_id']}"
                    }
                    
                    # 构建保存路径
                    save_name = f"{result['title']}_{video['video_id']}.mp4"
                    save_name = re.sub(r'[\\/:*?"<>|]', '_', save_name)  # 替换非法字符
                    save_path = str(download_dir / save_name)
                    
                    # 检查是否已下载
                    if os.path.exists(save_path):
                        result.update({
                            'status': 'skipped',
                            'error': '文件已存在',
                            'path': save_path
                        })
                    else:
                        # 下载视频
                        logger.info(f"开始下载视频: {result['title']}")
                        if self.download_video(video['play_url'], save_path):
                            result.update({
                                'status': 'success',
                                'path': save_path
                            })
                        else:
                            result.update({
                                'status': 'failed',
                                'error': '下载失败'
                            })
                    
                    results.append(result)
                
                # 检查是否还有更多视频
                if next_cursor == 0 or next_cursor == max_cursor:
                    has_more = False
                max_cursor = next_cursor
                
                # 添加延迟，避免请求过快
                if has_more:
                    time.sleep(random.uniform(1, 3))
            
            return results
            
        except Exception as e:
            logger.exception(f"批量下载失败: {str(e)}")
            raise 

    def _get_api_params(self) -> Dict[str, str]:
        """获取API请求需要的特殊参数
        
        Returns:
            Dict[str, str]: 包含msToken、X-Bogus、_signature等参数
        """
        try:
            # 从cookies中获取msToken
            ms_token = self.session.cookies.get('msToken', '')
            
            # 从localStorage中获取X-Bogus和_signature
            # 这里需要执行JavaScript获取，暂时使用空值
            x_bogus = ''
            signature = ''
            
            # 获取设备ID
            did = self.session.cookies.get('passport_did', '')
            if not did:
                did = f"7242624631965951489_{int(time.time() * 1000)}"
            
            params = {
                'device_platform': 'webapp',
                'aid': '6383',
                'channel': 'channel_pc_web',
                'count': '20',
                'version_code': '170400',
                'version_name': '17.4.0',
                'cookie_enabled': 'true',
                'screen_width': '1920',
                'screen_height': '1080',
                'browser_language': 'zh-CN',
                'browser_platform': 'Win32',
                'browser_name': 'Chrome',
                'browser_version': '120.0.0.0',
                'browser_online': 'true',
                'engine_name': 'Blink',
                'engine_version': '120.0.0.0',
                'os_name': 'Windows',
                'os_version': '10',
                'cpu_core_num': '16',
                'device_memory': '8',
                'platform': 'PC',
                'downlink': '10',
                'effective_type': '4g',
                'round_trip_time': '50',
                'webid': did,
                'msToken': ms_token,
                'X-Bogus': x_bogus,
                '_signature': signature
            }
            
            return params
        except Exception as e:
            logger.error(f"获取API参数失败: {str(e)}")
            return {} 