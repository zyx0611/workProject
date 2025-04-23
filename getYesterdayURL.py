import datetime
import time
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from contextlib import contextmanager

# 获取日期，用于模糊查询
def get_yesterday():
    now = time.time()
    yesterdaySeconds = now - 86400
    yesterday = datetime.date.fromtimestamp(yesterdaySeconds)
    print(yesterday)
    return yesterday

@contextmanager
def getConnection():
    # 加载 .env 文件中的环境变量
    load_dotenv()
    # 从环境变量中读取配置
    host = os.getenv('MONGO_HOST')
    port = int(os.getenv('MONGO_PORT'))
    username = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASS')
    target_db = os.getenv('MONGO_DB_NAME')

    # 构建 MongoDB 连接字符串
    uri = f"mongodb://{username}:{password}@{host}:{port}/{target_db}"
    # 调试：打印最终 URI（确保无语法错误）
    print("正在连接 URI:", uri)
    # 创建 MongoClient 实例
    client = MongoClient(uri)
    # 连接指定数据库
    db = client[target_db]
    try:
        yield db
    finally:
        client.close()
        print("连接关闭成功")

def get_resultTable():
    yesterday = get_yesterday()
    output_field = "keyword_sha256"
    try:
        with getConnection() as db:
            # 列出数据库下的集合列表
            print(db.list_collection_names())
            # 接指定集合
            collection = db['content']
            # 查询条件：查找指定字段
            query = { "date": { "$regex": f"{yesterday}", "$options": "i" } , "generated": True}
            # res = collection.find_one(query).get("keyword_sha256")
            res = collection.find(query,{output_field: 1})
            # print(res)

            # 提取结果
            output = [doc[output_field] for doc in res if output_field in doc]

            # 只取前10条数据,方便调试
            output = output[:10]

            # 读取CSV生成URL
            with open('yesterdayURL.csv', 'w', newline='', encoding='utf-8') as f:
                for item in output:
                    url = f"https://infohivehub.com/zh-CN/details/{item}\n"
                    f.write(url)

    except Exception as e:
        print(f"连接失败: {e}")

if __name__ == "__main__":
    get_resultTable()
