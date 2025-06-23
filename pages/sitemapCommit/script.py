import requests

SITEMAP_URL = ""

SEARCH_ENGINES = {
    "google": f"https://www.google.com/ping?sitemap={SITEMAP_URL}",
    "bing": f"https://www.bing.com/ping?sitemap={SITEMAP_URL}",
}

def submit_sitemap():
    for name, url in SEARCH_ENGINES.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"{name}提交成功:{url}")
            else:
                print(f"{url}提交{name}失败：状态码 {response.status_code}")
        except Exception as e:
            print(f"{url}请求{name}报错：{e}")

if __name__ == "__main__":
    submit_sitemap()
