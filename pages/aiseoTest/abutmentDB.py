import asyncio
import aiohttp
from pymongo import MongoClient
import subprocess
import ssl
import sys
import os

from torchvision.models import SqueezeNet1_0_Weights

# MongoDB 连接
client = MongoClient("mongodb://readuser:Read0nly!2025@13.229.95.250:27017/seo_ai")
db = client["seo_ai"]
collection = db["content"]
results_col = db["check_results"]


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 伪造网页 URL
def build_url(article_id):
    return f"https://infohivehub.com/zh-CN/details/{article_id}"

# 网页内容检测逻辑（可调用你已有的检测方法）
async def analyze_page(session, url, article_id):
    try:
        async with session.get(url, timeout=10, ssl=ssl_context) as resp:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            os.chdir(project_root)
            test_file = "tests/test_aiseo.py"

            cmd = [
                sys.executable,
                "-m", "pytest",
                test_file,
                f"--url={url}",
                "-s", "-v",
                "--alluredir=allure-results",
            ]

            # ✅ 改为异步子进程执行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            print(stdout.decode())
            if stderr:
                print("❌ 错误输出：", stderr.decode())

    except Exception as e:
        print(f"❌ {url} 异常：{e}")

# 协程任务调度
async def main(batch_size=1, max_concurrent=3):
    skip = 0
    while skip < 3:
        query = {"generated": True}
        articles = list(collection.find(query).skip(skip).limit(batch_size))
        if not articles:
            break
        tasks = []
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            for article in articles:
                article_id = article["keyword_sha256"]
                url = build_url(article_id)
                tasks.append(analyze_page(session, url, article_id))
            await asyncio.gather(*tasks)
        skip += batch_size
        print(f"✅ 已处理 {skip} 篇文章")

asyncio.run(main())