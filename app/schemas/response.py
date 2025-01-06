"""
响应数据Schema
"""
from marshmallow import Schema, fields


class ErrorSchema(Schema):
    """错误响应Schema"""
    code = fields.Integer(required=True)
    message = fields.String(required=True)


class UserSchema(Schema):
    """用户信息Schema"""
    user_id = fields.String(required=True)
    nickname = fields.String(required=True)
    avatar = fields.String(required=True)
    signature = fields.String(required=False, allow_none=True)
    following_count = fields.Integer(required=True)
    follower_count = fields.Integer(required=True)
    liked_count = fields.Integer(required=True)


class VideoSchema(Schema):
    """视频信息Schema"""
    video_id = fields.String(required=True)
    title = fields.String(required=True)
    cover = fields.String(required=True)
    play_url = fields.String(required=True)
    duration = fields.Integer(required=True)
    create_time = fields.DateTime(required=True)
    like_count = fields.Integer(required=True)
    comment_count = fields.Integer(required=True)
    share_count = fields.Integer(required=True)


class VideoListSchema(Schema):
    """视频列表Schema"""
    videos = fields.List(fields.Nested(VideoSchema), required=True)
    has_more = fields.Boolean(required=True)
    cursor = fields.String(required=True) 