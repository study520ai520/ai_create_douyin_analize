"""
抖音视频下载器核心模块
"""
import os
import time
import json
import re
import random
import pickle
from typing import Dict, List, Optional, Tuple
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class DouyinDownloader:
    """抖音下载器"""

    # 用户代理列表
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0'
    ]

    def __init__(self, use_proxy: bool = False, proxy_url: str = None):
        """初始化下载器"""
        self.session = self._create_session()
        self.cookies_file = Path("data/cookies.pkl")
        
        # 加载或初始化Cookies
        self._load_cookies()
        
        # 设置代理
        if use_proxy:
            if proxy_url:
                self.session.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                # 使用默认代理
                self.session.proxies = {
                    'http': 'http://127.0.0.1:7890',
                    'https': 'http://127.0.0.1:7890'
                }

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
            'User-Agent': random.choice(self.USER_AGENTS),
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
        """发送请求"""
        try:
            # 更新请求头
            self._update_headers()
            
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            # 发送请求
            response = self.session.request(method, url, timeout=10, **kwargs)
            
            # 保存新的Cookies
            if response.cookies:
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

    def get_user_info(self, url: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            response = self._make_request('GET', url)
            if not response or response.status_code != 200:
                logger.error(f"获取用户页面失败: {response.status_code if response else 'No response'}")
                return None

            # 解析页面
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取用户信息
            script_data = soup.find('script', id='RENDER_DATA')
            if script_data:
                data = json.loads(script_data.string)
                user_data = data.get('user', {})
                return {
                    'user_id': user_data.get('uid'),
                    'nickname': user_data.get('nickname'),
                    'signature': user_data.get('signature'),
                    'following_count': user_data.get('following_count'),
                    'follower_count': user_data.get('follower_count'),
                    'liked_count': user_data.get('total_favorited')
                }
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None

    def get_video_list(self, user_id: str, max_cursor: int = 0) -> Tuple[List[Dict], int]:
        """获取视频列表"""
        try:
            api_url = f"https://www.douyin.com/web/api/v2/aweme/post/?user_id={user_id}&count=20&max_cursor={max_cursor}"
            response = self._make_request('GET', api_url)
            
            if not response or response.status_code != 200:
                logger.error(f"获取视频列表失败: {response.status_code if response else 'No response'}")
                return [], 0

            data = response.json()
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
            
            return videos, next_cursor
        except Exception as e:
            logger.error(f"获取视频列表失败: {str(e)}")
            return [], 0

    def download_video(self, video_url: str, save_path: str) -> bool:
        """下载视频"""
        try:
            # 获取视频内容
            response = self._make_request('GET', video_url, stream=True)
            if not response or response.status_code != 200:
                logger.error(f"下载视频失败: {response.status_code if response else 'No response'}")
                return False

            # 保存视频
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024  # 1MB
            
            with open(save_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)

            logger.info(f"视频下载完成: {save_path}")
            return True
        except Exception as e:
            logger.error(f"下载视频失败: {str(e)}")
            return False

    def download_all_videos(self, user_url: str, save_dir: str = None) -> List[Dict]:
        """下载用户的所有视频"""
        try:
            # 1. 解析用户URL
            standard_url = self.parse_url(user_url)
            if not standard_url:
                raise Exception("无效的用户URL")
            
            # 2. 获取用户信息
            user_info = self.get_user_info(standard_url)
            if not user_info:
                raise Exception("获取用户信息失败")
            
            # 3. 创建保存目录
            if save_dir is None:
                save_dir = os.path.join("data/downloads", user_info['nickname'])
            os.makedirs(save_dir, exist_ok=True)
            
            # 4. 获取并下载视频
            download_results = []
            max_cursor = 0
            
            while True:
                videos, next_cursor = self.get_video_list(user_info['user_id'], max_cursor)
                if not videos:
                    break
                
                for video in videos:
                    try:
                        # 构建保存路径
                        video_name = f"{video['title'][:50]}_{video['video_id']}.mp4"
                        video_name = re.sub(r'[\\/:*?"<>|]', '_', video_name)  # 移除非法字符
                        save_path = os.path.join(save_dir, video_name)
                        
                        # 如果文件已存在，跳过下载
                        if os.path.exists(save_path):
                            logger.info(f"视频已存在，跳过下载: {save_path}")
                            download_results.append({
                                'video_id': video['video_id'],
                                'title': video['title'],
                                'status': 'skipped',
                                'path': save_path
                            })
                            continue
                        
                        # 下载视频
                        if self.download_video(video['play_url'], save_path):
                            download_results.append({
                                'video_id': video['video_id'],
                                'title': video['title'],
                                'status': 'success',
                                'path': save_path
                            })
                        else:
                            raise Exception("下载失败")
                        
                        # 添加随机延时
                        time.sleep(random.uniform(1, 3))
                    except Exception as e:
                        logger.error(f"下载视频失败: {video['video_id']}, 错误: {str(e)}")
                        download_results.append({
                            'video_id': video['video_id'],
                            'title': video['title'],
                            'status': 'failed',
                            'error': str(e)
                        })
                
                if not next_cursor or next_cursor == max_cursor:
                    break
                max_cursor = next_cursor
            
            return download_results
        except Exception as e:
            logger.error(f"批量下载失败: {str(e)}")
            raise 