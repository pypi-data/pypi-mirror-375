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

    @classmethod
    def is_http_url(cls, url: str) -> bool:
        """
        判断是否为http链接
        """
        return url.startswith("http://") or url.startswith("https://")

    @classmethod
    def transfer_url(cls, url: str):
        """
        如果是http链接则提取出文件名
        如果是本地路径则直接返回
        """
        if url and cls.is_http_url(url):
            return cls.extract_url_filename(url)
        else:
            return url