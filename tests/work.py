from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import uvicorn

async def login_both_systems(username: str, password: str):
    # 1. 登录中央系统（假设你已有）
    # 2. 登录子服务 A
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://127.0.0.1:8000/api/users/login", json={
            "username": username,
            "password": password
        })
        if resp.status_code == 200:
            cookies = resp.cookies
            # 保存 cookie（或 token）到中央系统会话中
            return cookies
        else:
            raise HTTPException(status_code=500, detail="子服务 A 登录失败")

app = FastAPI()

# 伪代码：从用户会话中取出子服务 A 登录 cookie
def get_subservice_a_cookie_from_session(user_id):
    # 实际应用中从 Redis/Session 数据库中取
    return {"sessionid": "abc123"}


# @app.api_route("/subservice-a/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@app.api_route("/subservice-a", methods=["GET", "POST", "PUT", "DELETE"])
# async def proxy_to_subservice_a(path: str, request: Request):
async def proxy_to_subservice_a(request: Request):
    # subservice_a_url = f"http://subservice-a.local/{path}"
    subservice_a_url = "http://localhost:8000/api/backends/text-completions/generate"

    headers = dict(request.headers)
    headers.pop("host", None)  # 避免 host 冲突

    method = request.method
    print('request.method:', request.method)
    body = await request.body()

    # cookies = get_subservice_a_cookie_from_session(user_id="some_user")
    cookies = await login_both_systems('Admin', '12345678')

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method,
            subservice_a_url,
            headers=headers,
            content=body,
            cookies={
                'cookie': cookies
            }
        )

    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)

if __name__ == "__main__":
    uvicorn.run("httpxDemo:app", host="0.0.0.0", port=3333, reload=True)