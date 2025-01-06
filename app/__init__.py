"""
抖音视频下载工具
"""
from pathlib import Path

# 设置项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 设置数据目录
DATA_DIR = ROOT_DIR / 'data'
DOWNLOAD_DIR = DATA_DIR / 'downloads'
LOG_DIR = DATA_DIR / 'logs'

# 创建必要的目录
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
