import asyncio
from typing import  TypeVar

from huibiao_framework.utils.file_manage import AbstractAsyncFile

from loguru import logger

T = TypeVar("T", bound=AbstractAsyncFile)


class TempAsyncFileWrapper:
    def __init__(self, async_file: T, is_clean: bool=True):
        self.file: T = async_file
        self.is_clean = is_clean

    async def __aenter__(self) -> T:
        return self.file

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.is_clean:
            async def delete_file():
                try:
                    self.file.delete()
                except Exception as e:
                    logger.warning(
                        f"delete file {self.file.local_path} error, {e}"
                    )
            asyncio.create_task(delete_file())


