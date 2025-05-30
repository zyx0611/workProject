import requests
from bs4 import BeautifulSoup
import urllib.parse

def search_baidu_article(keyword):
    # 构造百度搜索 URL
    query = urllib.parse.quote(keyword)
    url = f"https://www.baidu.com/s?wd={query}"

    # 设置请求头模拟浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("请求失败：", e)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for item in soup.select('.result'):
        link_tag = item.select_one('a')
        if not link_tag:
            continue

        link = link_tag.get('href')
        title = link_tag.get_text(strip=True)

        # 过滤广告（百度广告链接常带有 "广告" 或跳转链接很短、带有 certain pattern）
        is_ad = item.select_one('.c-span-last') or '广告' in item.get_text()
        if is_ad:
            continue

        # 解析真实跳转链接
        try:
            real_url = requests.head(link, allow_redirects=True, headers=headers, timeout=5).url
        except requests.RequestException:
            continue

        results.append((title, real_url))

    if not results:
        print("没有找到有效结果")
        return None

    # 返回第一个最相关的非广告结果
    print("搜索结果：")
    print(f"标题: {results[0][0]}")
    print(f"链接: {results[0][1]}")
    return results[0]

# 示例调用
if __name__ == "__main__":
    keyword = "李白的诗歌分析"
    search_baidu_article(keyword)
