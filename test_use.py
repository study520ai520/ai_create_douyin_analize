"""
抖音视频下载工具使用示例
"""
import os
from pathlib import Path
from loguru import logger
from app.core.downloader import DouyinDownloader

# 设置项目根目录
ROOT_DIR = Path(__file__).parent

# 配置日志
LOG_DIR = ROOT_DIR / 'data' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger.add(LOG_DIR / "test.log", rotation="500 MB", retention="10 days", level="INFO")

def test_download_user_videos():
    """测试下载用户所有视频"""
    try:
        # 使用默认配置
        use_proxy = False
        proxy_url = None
        user_url = "https://www.douyin.com/user/MS4wLjABAAAAC8OzFMQUhcyt6GJhy0Tq5KX1kVM9jXoLzGDASFfEBn-shzaEQ_w3LBpT5uwQzbhA"
        
        logger.info(f"使用配置: use_proxy={use_proxy}, proxy_url={proxy_url}")
        logger.info(f"测试URL: {user_url}")
        
        downloader = DouyinDownloader(use_proxy=use_proxy, proxy_url=proxy_url)
        results = downloader.download_all_videos(user_url)
        
        logger.info(f"下载完成，总计: {len(results)} 个视频")
        
        # 统计下载结果
        success_count = len([r for r in results if r["status"] == "success"])
        failed_count = len([r for r in results if r["status"] == "failed"])
        skipped_count = len([r for r in results if r["status"] == "skipped"])
        
        logger.info(f"成功: {success_count}, 失败: {failed_count}, 跳过: {skipped_count}")
        
        # 输出失败的视频信息
        if failed_count > 0:
            logger.warning("失败的视频列表:")
            for result in results:
                if result["status"] == "failed":
                    logger.warning(f"视频ID: {result['video_id']}, 标题: {result['title']}, 错误: {result['error']}")
    
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    logger.info("=== 抖音视频下载工具 ===")
    test_download_user_videos() 