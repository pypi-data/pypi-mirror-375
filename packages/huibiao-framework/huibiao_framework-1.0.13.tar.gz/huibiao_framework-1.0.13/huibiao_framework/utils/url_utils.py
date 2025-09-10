import os
from urllib.parse import urlparse, unquote


class UrlUtils:
    @classmethod
    def extract_url_filename(cls, url: str) -> str:
        """
        从下载链接中获取文件名，去除其他参数
        """
        parsed = urlparse(url)
        return unquote(os.path.basename(parsed.path))