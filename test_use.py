"""
抖音视频下载工具使用示例
"""
import os
import time
from typing import Dict, List

import requests
from loguru import logger

# 配置日志
logger.add("data/logs/test.log", rotation="500 MB", retention="10 days", level="INFO")

class DouyinDownloader:
    """抖音下载器"""

    def __init__(self, base_url: str = "http://localhost:5000/api/v1"):
        """初始化下载器"""
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def parse_user_url(self, url: str) -> Dict:
        """解析用户URL"""
        logger.info(f"开始解析用户URL: {url}")
        response = requests.post(
            f"{self.base_url}/parse",
            json={"url": url},
            headers=self.headers
        )
        if response.status_code != 200:
            logger.error(f"URL解析失败: {response.text}")
            raise Exception(f"URL解析失败: {response.text}")
        return response.json()

    def get_user_info(self, user_id: str) -> Dict:
        """获取用户信息"""
        logger.info(f"获取用户信息: {user_id}")
        response = requests.get(
            f"{self.base_url}/user/{user_id}",
            headers=self.headers
        )
        if response.status_code != 200:
            logger.error(f"获取用户信息失败: {response.text}")
            raise Exception(f"获取用户信息失败: {response.text}")
        return response.json()

    def get_user_videos(self, user_id: str, cursor: str = None) -> Dict:
        """获取用户视频列表"""
        logger.info(f"获取用户视频列表: {user_id}, cursor: {cursor}")
        params = {"cursor": cursor} if cursor else {}
        response = requests.get(
            f"{self.base_url}/user/{user_id}/videos",
            params=params,
            headers=self.headers
        )
        if response.status_code != 200:
            logger.error(f"获取视频列表失败: {response.text}")
            raise Exception(f"获取视频列表失败: {response.text}")
        return response.json()

    def download_video(self, video_id: str, save_path: str = None) -> Dict:
        """下载视频"""
        logger.info(f"下载视频: {video_id}, 保存路径: {save_path}")
        data = {"video_id": video_id}
        if save_path:
            data["save_path"] = save_path
        response = requests.post(
            f"{self.base_url}/download",
            json=data,
            headers=self.headers
        )
        if response.status_code != 200:
            logger.error(f"视频下载失败: {response.text}")
            raise Exception(f"视频下载失败: {response.text}")
        return response.json()

    def download_all_videos(self, user_url: str, save_dir: str = None) -> List[Dict]:
        """下载用户的所有视频"""
        try:
            # 1. 解析用户URL
            parse_result = self.parse_user_url(user_url)
            user_id = parse_result["data"]["url"].split("/")[-1]
            
            # 2. 获取用户信息
            user_info = self.get_user_info(user_id)
            nickname = user_info["data"]["nickname"]
            
            # 3. 创建保存目录
            if save_dir is None:
                save_dir = os.path.join("data/downloads", nickname)
            os.makedirs(save_dir, exist_ok=True)
            
            # 4. 获取所有视频
            download_results = []
            cursor = None
            while True:
                videos_result = self.get_user_videos(user_id, cursor)
                videos = videos_result["data"]["videos"]
                
                # 下载每个视频
                for video in videos:
                    try:
                        video_save_path = os.path.join(save_dir, f"{video['title']}.mp4")
                        result = self.download_video(video["video_id"], video_save_path)
                        download_results.append({
                            "video_id": video["video_id"],
                            "title": video["title"],
                            "status": "success",
                            "task_id": result["data"]["task_id"]
                        })
                        # 添加延时，避免请求过于频繁
                        time.sleep(1)
                    except Exception as e:
                        logger.error(f"下载视频失败: {video['video_id']}, 错误: {str(e)}")
                        download_results.append({
                            "video_id": video["video_id"],
                            "title": video["title"],
                            "status": "failed",
                            "error": str(e)
                        })
                
                # 检查是否还有更多视频
                if not videos_result["data"]["has_more"]:
                    break
                cursor = videos_result["data"]["cursor"]
            
            return download_results
            
        except Exception as e:
            logger.error(f"批量下载失败: {str(e)}")
            raise

def test_download_single_video():
    """测试下载单个视频"""
    downloader = DouyinDownloader()
    video_id = "7123456789"  # 替换为实际的视频ID
    try:
        result = downloader.download_video(video_id)
        logger.info(f"下载成功: {result}")
    except Exception as e:
        logger.error(f"下载失败: {str(e)}")

def test_download_user_videos():
    """测试下载用户所有视频"""
    downloader = DouyinDownloader()
    # 替换为实际的用户主页URL
    user_url = "https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI"
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
    # 测试用例1：下载单个视频
    logger.info("=== 测试下载单个视频 ===")
    test_download_single_video()
    
    # 测试用例2：下载用户所有视频
    logger.info("=== 测试下载用户所有视频 ===")
    test_download_user_videos() 