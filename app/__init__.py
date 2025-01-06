"""
抖音视频下载工具 Flask应用
"""
from flask import Flask
from flask_cors import CORS
from loguru import logger

from app.api import api_bp
from app.config import Config


def create_app(config_class=Config):
    """
    创建Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化CORS
    CORS(app)

    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # 配置日志
    logger.add(
        "data/logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )

    @app.route('/health')
    def health_check():
        """健康检查接口"""
        return {'status': 'ok'}

    return app
