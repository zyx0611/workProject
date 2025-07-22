import asyncio
import json
import time
import httpx
from pages.aiseoTest.SignatureUtils import SignatureUtils

class AsyncAPIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(timeout))
        self.params = {}
        self.headers = {}
        self.access_secret =  ""
        self.access_key =  ""

    def set_header(self, key: str, value: str):
        """添加请求头"""
        self.headers[key] = value
        return self
    def set_access_secret(self, access_secret: str):
        """添加请求头"""
        self.access_secret = access_secret
        return self
    def set_access_key(self, access_key: str):
        """添加请求头"""
        self.access_key = access_key
        self.add_param("access_key", access_key)
        return self

    def add_param(self, key: str, value):
        """添加请求参数"""
        self.params[key] = value
        if type(value) == dict:
            self.params[key] = json.dumps( value)
        return self

    def sign_params(self):
        """使用sign_utils生成签名"""
        self.set_header("X-API-Sign", SignatureUtils.get_salted_signature(self.params, self.access_secret))
        return self
    def set_default_head(self):
        self.set_header("Authorization","Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJydDAxIiwiZXhwIjoxNzU5MjAxNzQ5fQ.v4mBeR8b_qdppG72y2FfQQZVtf_7VCUkRBq2PyIgdEw")
        return self

    async def send_request(self, endpoint: str, method: str = "GET"):
        """发送异步 JSON 请求，并设置超时"""
        url = f"{self.base_url}{endpoint}"
        response = await self.client.request(
            method=method,
            url=url,
            params=self.params if method == "GET" else None,
            data=self.params if method == "POST" else None,
            headers=self.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.text


    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


async def main():
    # 调用示例

    client = AsyncAPIClient(base_url="https://comic.frw.cnhivehub.com", timeout=20)
    (client
     .set_access_secret("user2") # 添加 access_secret（必填）

     .set_access_key("1234qwer") # 添加 access_key（必填）

     .set_default_head())
    response = (
        client
            .add_param("flow_name", "img2img_inpaint")
            .add_param("source_urls",{"source": "https://ip:port/view?filename=girl.jpeg","mask_source": "https://ip:port/view?filename=canvas.png"})
            .add_param("prompt_config",  {"refine_negative": "blurry, low quality, distortion","refine_positive": "bikini，blue color"})
            .add_param("timestamp", int(time.time()))  # 添加时间戳（必填）

            .sign_params() # 使用签名工具生成签名

            .send_request("/api/models/generate/process", method="POST")
    )
    result = await response
    print(f"result: {result}")

# 启动事件循环

if __name__ == "__main__":
    asyncio.run(main())