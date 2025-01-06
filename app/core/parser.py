"""
抖音URL解析模块
负责处理和验证抖音用户主页URL，支持长短链接的解析
"""
import re
from typing import Optional, Tuple
import requests
from loguru import logger


class URLParser:
    """抖音URL解析器"""
    
    # 抖音URL正则表达式
    DOUYIN_URL_PATTERNS = [
        r'https?://(?:www\.)?douyin\.com/user/([^/?]+)',  # 标准用户主页
        r'https?://v\.douyin\.com/([^/?]+)',              # 短链接
    ]

    def __init__(self):
        """初始化解析器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def parse_url(self, url: str) -> Optional[str]:
        """
        解析抖音URL，返回标准化的用户主页URL
        
        Args:
            url: 输入的URL字符串
            
        Returns:
            Optional[str]: 解析后的标准URL，解析失败返回None
        """
        try:
            # 1. 验证URL格式
            if not self._is_valid_url(url):
                logger.error(f"无效的URL格式: {url}")
                return None

            # 2. 处理短链接
            if 'v.douyin.com' in url:
                url = self._expand_short_url(url)
                if not url:
                    return None

            # 3. 提取用户ID
            user_id = self._extract_user_id(url)
            if not user_id:
                logger.error(f"无法提取用户ID: {url}")
                return None

            # 4. 返回标准化URL
            return f"https://www.douyin.com/user/{user_id}"

        except Exception as e:
            logger.error(f"URL解析失败: {str(e)}")
            return None

    def _is_valid_url(self, url: str) -> bool:
        """
        验证URL是否符合抖音链接格式
        """
        return any(re.match(pattern, url) for pattern in self.DOUYIN_URL_PATTERNS)

    def _expand_short_url(self, short_url: str) -> Optional[str]:
        """
        展开短链接为完整URL
        """
        try:
            response = self.session.head(short_url, allow_redirects=True)
            if response.status_code == 200:
                return response.url
            logger.error(f"短链接展开失败: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"短链接请求失败: {str(e)}")
            return None

    def _extract_user_id(self, url: str) -> Optional[str]:
        """
        从URL中提取用户ID
        """
        for pattern in self.DOUYIN_URL_PATTERNS:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None

    def validate_user_exists(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        验证用户是否存在
        
        Returns:
            Tuple[bool, Optional[str]]: (是否存在, 错误信息)
        """
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return True, None
            elif response.status_code == 404:
                return False, "用户不存在"
            else:
                return False, f"请求失败: {response.status_code}"
        except Exception as e:
            return False, f"验证失败: {str(e)}" 