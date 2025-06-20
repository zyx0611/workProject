import requests
from bs4 import BeautifulSoup
import urllib.parse

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "cookie": "MUID=3EF2F962DD9364543ACBECA1DC7965E0; ANON=A=D099E653DDB16EEFEE604837FFFFFFFF&E=1f22&W=4; NAP=V=1.9&E=1ec8&C=mLP9S-HOi_fBLUVGBn1_Z9DvXl0ngZZUmzp0PNA3gZIDCcdBfxBuhw&W=4; MUIDB=3EF2F962DD9364543ACBECA1DC7965E0; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=70FB36C1D51C4F76A06A5631F1B97DE9&dmnchg=1; _UR=QS=0&TQS=0&Pn=0; BFBUSR=BFBHP=0; SRCHUSR=DOB=20250529&DS=1; _HPVN=CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyNS0wNS0yOVQwMDowMDowMFoiLCJJb3RkIjowLCJHd2IiOjAsIlRucyI6MCwiRGZ0IjpudWxsLCJNdnMiOjAsIkZsdCI6MCwiSW1wIjoyLCJUb2JuIjowfQ==; SRCHHPGUSR=SRCHLANG=zh-Hans&DM=0&BRW=W&BRH=M&CW=1440&CH=778&SCW=1440&SCH=778&DPR=2.0&UTC=480&PV=15.4.0; _RwBf=r=0&ilt=1&ihpd=1&ispd=0&rc=0&rb=0&rg=200&pc=0&mtu=0&rbb=0&clo=0&v=1&l=2025-05-28T07:00:00.0000000Z&lft=0001-01-01T00:00:00.0000000&aof=0&ard=0001-01-01T00:00:00.0000000&rwdbt=0&rwflt=0&rwaul2=0&g=&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2025-05-29T06:38:47.1503266+00:00&rwred=0&wls=&wlb=&wle=&ccp=&cpt=&lka=0&lkt=0&aad=0&TH=&cid=0&gb=; ai_user=P/YuZ|2025-05-29T07:04:37.818Z"
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
