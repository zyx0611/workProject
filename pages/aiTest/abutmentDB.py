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
            test_file = "tests/test_ai.py"

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

# 基础指标
# title
# 是否包含关键词 ✅
# 是否有设置title标签 ✅
# 是否有设置h1标签的标题 ✅
# description
# 是否包含关键词 ✅
# 是否能表达当前网页的摘要
# 是否在120-160字符之间 ✅
# keywords
# 聚焦网页主要内容 ✅
# slug
# 网页唯一的可访问标识
# 足够语义化 ✅
# Canonical
# 可被搜索引擎引用的最佳URL（设置当前网页url即可，最权威）✅
# img
# 是否包含有图片嵌入（满足友好阅读体验）✅
# 重要指标
# 网页结构化
# 是否包含多级标签「h1, h2, h3...」✅
# 是否包含多个段落 ✅
# 关键词密度
# 各级标题中是否分布有「关键词、近义词」✅
# 各个段落中是否有多次出现「关键词、近义词」 ✅
# 外链
# 外链是否与当前页面具有相关性 ✅
# 外链是否能正常访问