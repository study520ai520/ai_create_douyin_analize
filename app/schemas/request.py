"""
请求数据验证Schema
"""
from marshmallow import Schema, fields, validate


class URLSchema(Schema):
    """URL请求Schema"""
    url = fields.String(required=True, validate=validate.URL(error="无效的URL格式"))


class DownloadSchema(Schema):
    """下载请求Schema"""
    video_id = fields.String(required=True)
    save_path = fields.String(required=False) 