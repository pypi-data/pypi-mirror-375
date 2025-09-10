import asyncio

from huibiao_framework.utils.file_manage import BytesAsyncFile


async def run():
    file = BytesAsyncFile(
        wget_link="gz4oss.xstore.ctyun.cn/biaoshu2refactor/example_data/huibiao-file-infer-service/pdf_parse/%E9%A1%B9%E7%9B%AEAA%E6%8A%A5%E4%BB%B7%E9%83%A8%E5%88%86A%E6%96%87%E4%BB%B6%281%29%281%29%20%281%29.pdf"
    )

    await file.wget()


asyncio.run(run())