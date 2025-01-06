"""
API路由定义
"""
from flask import jsonify, request
from loguru import logger

from app.api import api_bp
from app.core.parser import URLParser
from app.schemas.request import URLSchema
from app.schemas.response import ErrorSchema, UserSchema


@api_bp.route('/parse', methods=['POST'])
def parse_url():
    """
    解析抖音用户URL
    ---
    请求体:
    {
        "url": "https://www.douyin.com/user/xxx"
    }
    """
    try:
        # 验证请求数据
        data = URLSchema().load(request.json)
        url = data['url']

        # 解析URL
        parser = URLParser()
        parsed_url = parser.parse_url(url)
        
        if not parsed_url:
            return ErrorSchema().dump({
                'code': 400,
                'message': '无效的URL格式'
            }), 400

        # 验证用户是否存在
        exists, error = parser.validate_user_exists(parsed_url)
        if not exists:
            return ErrorSchema().dump({
                'code': 404,
                'message': error or '用户不存在'
            }), 404

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'url': parsed_url
            }
        })

    except Exception as e:
        logger.exception("URL解析失败")
        return ErrorSchema().dump({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@api_bp.route('/user/<user_id>', methods=['GET'])
def get_user_info(user_id):
    """
    获取用户信息
    """
    try:
        # TODO: 实现用户信息获取逻辑
        return UserSchema().dump({
            'user_id': user_id,
            'nickname': '测试用户',
            'avatar': 'https://example.com/avatar.jpg',
            'signature': '这是一个测试签名',
            'following_count': 100,
            'follower_count': 1000,
            'liked_count': 10000
        })

    except Exception as e:
        logger.exception("获取用户信息失败")
        return ErrorSchema().dump({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@api_bp.route('/user/<user_id>/videos', methods=['GET'])
def get_user_videos(user_id):
    """
    获取用户视频列表
    """
    try:
        # TODO: 实现视频列表获取逻辑
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'videos': [],
                'has_more': False,
                'cursor': ''
            }
        })

    except Exception as e:
        logger.exception("获取视频列表失败")
        return ErrorSchema().dump({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@api_bp.route('/download', methods=['POST'])
def download_video():
    """
    下载视频
    ---
    请求体:
    {
        "video_id": "xxx",
        "save_path": "optional/path/to/save"
    }
    """
    try:
        # TODO: 实现视频下载逻辑
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'task_id': 'download_task_123',
                'status': 'pending'
            }
        })

    except Exception as e:
        logger.exception("视频下载失败")
        return ErrorSchema().dump({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500 