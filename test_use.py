"""
抖音视频下载工具 - 线下版本
"""
import os
import time
import json
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from loguru import logger

# 配置日志
logger.add("data/logs/test.log", rotation="500 MB", retention="10 days", level="INFO")

class DouyinDownloader:
    """抖音下载器"""

    def __init__(self):
        """初始化下载器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.douyin.com/'
        })
        # 设置代理（如果需要）
        # self.session.proxies = {
        #     'http': 'http://127.0.0.1:7890',
        #     'https': 'http://127.0.0.1:7890'
        # }

    def parse_url(self, url: str) -> Optional[str]:
        """解析抖音URL，支持短链接"""
        try:
            if 'v.douyin.com' in url:
                response = self.session.head(url, allow_redirects=True)
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
            response = self.session.get(url)
            if response.status_code != 200:
                logger.error(f"获取用户页面失败: {response.status_code}")
                return None

            # 解析页面
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取用户信息（实际实现需要根据抖音页面结构调整）
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
            response = self.session.get(api_url)
            
            if response.status_code != 200:
                logger.error(f"获取视频列表失败: {response.status_code}")
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
            response = self.session.get(video_url, stream=True)
            if response.status_code != 200:
                logger.error(f"下载视频失败: {response.status_code}")
                return False

            # 保存视频
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1KB
            
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
                        
                        # 添加延时
                        time.sleep(1)
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

def test_download_user_videos():
    """测试下载用户所有视频"""
    downloader = DouyinDownloader()
    # 替换为实际的用户主页URL
    user_url = input("请输入抖音用户主页URL: ").strip()
    
    try:
        results = downloader.download_all_videos(user_url)
        logger.info(f"下载完成，总计: {len(results)} 个视频")
        
        # 统计下载结果
        success_count = len([r for r in results if r["status"] == "success"])
        failed_count = len([r for r in results if r["status"] == "failed"])
        logger.info(f"成功: {success_count}, 失败: {failed_count}")
        
        # 输出失败的视频信息
        if failed_count > 0:
            logger.warning("失败的视频列表:")
            for result in results:
                if result["status"] == "failed":
                    logger.warning(f"视频ID: {result['video_id']}, 标题: {result['title']}, 错误: {result['error']}")
    
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")

if __name__ == "__main__":
    logger.info("=== 抖音视频下载工具 ===")
    test_download_user_videos() 