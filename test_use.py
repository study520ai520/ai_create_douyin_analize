"""
抖音视频下载工具使用示例
"""
from loguru import logger
from app.core.downloader import DouyinDownloader

# 配置日志
logger.add("data/logs/test.log", rotation="500 MB", retention="10 days", level="INFO")

def test_download_user_videos():
    """测试下载用户所有视频"""
    # 询问是否使用代理
    use_proxy = input("是否使用代理？(y/n): ").strip().lower() == 'y'
    proxy_url = None
    if use_proxy:
        proxy_url = input("请输入代理地址（直接回车使用默认代理http://127.0.0.1:7890）: ").strip()
        if not proxy_url:
            proxy_url = 'http://127.0.0.1:7890'
    
    downloader = DouyinDownloader(use_proxy=use_proxy, proxy_url=proxy_url)
    
    # 输入用户URL
    user_url = input("请输入抖音用户主页URL: ").strip()
    
    try:
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

if __name__ == "__main__":
    logger.info("=== 抖音视频下载工具 ===")
    test_download_user_videos() 