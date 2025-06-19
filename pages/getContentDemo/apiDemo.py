import requests
from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# options = Options()
# options.add_argument('--headless')  # 设置为无头模式
# options.add_argument('--disable-gpu')  # 禁用GPU加速（可选）
# options.add_argument('--window-size=1920x1080')
# edge = webdriver.Chrome(options=options)

def is_valid_url(url, title):
    if not url:
        return False
    if 'baidu.com' in url:
        return False
    if '广告' in title or '推广' in title:
        return False
    if len(url) < 10:
        return False
    return True

def check_page_quality(url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return False
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(strip=True)
        # edge.get(url)
        # # 等待页面完全加载（readyState == "complete"）
        # WebDriverWait(edge, 10).until(
        #     lambda d: d.execute_script("return document.readyState") == "complete"
        # )
        #
        # # 等待某个具体元素出现，例如 div.content（你可以替换为你目标元素）
        # element = WebDriverWait(edge, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "div.content"))
        # )
        if len(text) < 200:
            return False
        return True
    except Exception:
        return False

def search_baidu_article(keyword):
    query = urllib.parse.quote(keyword)
    url = f"https://www.bing.com/search?q={query}"

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

    for item in soup.select('li.b_algo'):
        link_tag = item.select_one('a')
        if not link_tag:
            continue

        link = link_tag.get('href')
        title = link_tag.get_text(strip=True)

        # 过滤广告
        if '广告' in item.get_text():
            continue

        try:
            real_url = requests.head(link, allow_redirects=True, headers=headers, timeout=5).url
        except requests.RequestException:
            continue

        if not is_valid_url(real_url, title):
            continue

        results.append((title, real_url))

    if not results:
        print("没有找到有效结果")
        return None

    # 过滤页面质量
    valid_results = []
    for title, real_url in results:
        if check_page_quality(real_url, headers):
            valid_results.append((title, real_url))

    if not valid_results:
        print("没有找到符合质量要求的链接")
        return None

    # 简单按标题和关键词相关度排序
    valid_results.sort(key=lambda x: keyword in x[0], reverse=True)

    print("搜索结果：")
    print(f"标题: {valid_results[0][0]}")
    print(f"链接: {valid_results[0][1]}")
    return valid_results[0]

if __name__ == "__main__":
    keywords = ['人工智能写作', '内容生成', '技术挑战']
    for keyword in keywords:
        search_baidu_article(keyword)

        "语言流畅性","情节合理性","角色塑造","结构完整性","创造力与新颖性","合规与伦理性"
