"""
URL解析模块的测试用例
"""
import pytest
from app.core.parser import URLParser


@pytest.fixture
def parser():
    """创建URLParser实例"""
    return URLParser()


def test_valid_user_url(parser):
    """测试标准用户主页URL解析"""
    url = "https://www.douyin.com/user/MS4wLjABAAAAKqxCy6CqgBOqf_Gc3W8_pKrwfqkWaK9PNy_RzHiXpKI"
    result = parser.parse_url(url)
    assert result == url


def test_short_url(parser):
    """测试短链接解析"""
    url = "https://v.douyin.com/abcd123/"
    result = parser.parse_url(url)
    # 注意：这里的断言依赖于实际的短链接重定向结果
    assert result is not None


def test_invalid_url(parser):
    """测试无效URL"""
    invalid_urls = [
        "https://example.com",
        "not_a_url",
        "https://douyin.com/invalid/path",
    ]
    for url in invalid_urls:
        assert parser.parse_url(url) is None


def test_url_validation(parser):
    """测试URL格式验证"""
    valid_urls = [
        "https://www.douyin.com/user/123456",
        "http://douyin.com/user/123456",
        "https://v.douyin.com/abcd123/",
    ]
    for url in valid_urls:
        assert parser._is_valid_url(url) is True 