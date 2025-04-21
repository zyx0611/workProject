import asyncio
import aiohttp
from pymongo import MongoClient
import subprocess
import ssl
import sys
import os

# MongoDB 连接
client = MongoClient("mongodb://readuser:Read0nly!2025@13.229.95.250:27017/seo_ai")
db = client["seo_ai"]
collection = db["keywords"]
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
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            os.chdir(project_root)

            test_file = "tests/test_aiseo.py"

            cmd = [
                sys.executable,  # 使用当前 Python 解释器
                "-m", "pytest",  # 调用 pytest 模块，避免直接调用命令
                test_file,
                f"--url={url}",
                "-s", "-v"
            ]

            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            print(result.stdout)
            print(result.stderr)

            # results_col.update_one(
            #     {"article_id": article_id},
            #     {"$set": {
            #         "url": url,
            #         "result": "异常" if suspicious else "正常"
            #     }},
            #     upsert=True
            # )
    except Exception as e:
        print(f"❌ {url} 异常：{e}")
        # results_col.update_one(
        #     {"article_id": article_id},
        #     {"$set": {
        #         "url": url,
        #         "result": "检测失败",
        #         "error": str(e)
        #     }},
        #     upsert=True
        # )

# 协程任务调度
async def main(batch_size=100, max_concurrent=10):
    skip = 0
    while True:
        articles = list(collection.find().skip(skip).limit(batch_size))
        if not articles:
            break
        tasks = []
        connector = aiohttp.TCPConnector(limit=max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            for article in articles:
                article_id = article["keyword_sha1"]
                url = build_url(article_id)
                tasks.append(analyze_page(session, url, article_id))
            await asyncio.gather(*tasks)
        skip += batch_size
        print(f"✅ 已处理 {skip} 篇文章")

asyncio.run(main())