"""
应用配置文件
"""
import os
from pathlib import Path


class Config:
    """基础配置类"""
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # 下载配置
    DOWNLOAD_DIR = BASE_DIR / 'data' / 'downloads'
    MAX_CONCURRENT_DOWNLOADS = 3
    CHUNK_SIZE = 1024 * 1024  # 1MB

    # 请求配置
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3

    # 日志配置
    LOG_DIR = BASE_DIR / 'data' / 'logs'
    LOG_LEVEL = 'INFO'

    # API配置
    API_TITLE = '抖音视频下载工具'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.2'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True


# 环境配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 