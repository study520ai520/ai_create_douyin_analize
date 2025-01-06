"""
应用入口文件
"""
import os
from app import create_app
from app.config.settings import config

# 获取环境配置
env = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[env])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
