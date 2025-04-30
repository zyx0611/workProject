from selenium.webdriver.common.by import By
import nltk
from nltk.stem import PorterStemmer
import re
from bs4 import BeautifulSoup
from soupsieve.util import lower
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor
import time
from pages.aiseoTest.compliance import analyze_headings_with_selenium

nltk.download('punkt')  # 只第一次需要

def extract_words_from_url(url):
    # 先按/切，再按-切
    parts = url.split('/')
    words = []
    for part in parts:
        words.extend(part.split('-'))
    return [word for word in words if word]

def clean_text(text):
    # 小写 + 去掉's 或 ’s
    text = text.lower()
    text = re.sub(r"(’s|'s)", "", text)  # 正则匹配两种撇号
    return text

def jump_problem(url, chrome):
    try:
        array = chrome.find_elements(By.TAG_NAME, 'a')
        for arr in array:
            src = arr.get_attribute("href")
            text = arr.text
            keyword = clean_text(text)
            keyword = set(keyword.split())
            stemmer = PorterStemmer()
            url_clean = clean_text(src)
            url_words = extract_words_from_url(url_clean)
            url_stems = set(stemmer.stem(word) for word in url_words)

            # 把关键词也stem处理
            keyword_stems = set(stemmer.stem(word.lower()) for word in keyword)

            if url_stems.isdisjoint(keyword_stems):
                print(f"关键词：{keyword}, 链接：{src}")
                return False
        return True
    except Exception as e:
        print(f"网页加载失败：{e}")

def keywords_contrast_and_title(url, chrome):
    title_text = chrome.title
    if title_text == '':
        print('title为空')
        return False
    keyword =  chrome.find_element(By.NAME, 'keywords')
    title_text = chrome.title
    title_text = lower(title_text)
    keyword_text = keyword.get_attribute('content')
    if not keyword_text in title_text:
        return False
    return True

def find_h1(chrome):
    try:
        h1 = chrome.find_elements(By.TAG_NAME, 'h1')
        for i in h1:
            if i.text != '':
                return True
        return False
    except Exception as e:
        print('获取h1标签失败：', e)

def description_keywords(chrome):
    description = chrome.find_element(By.NAME, 'description')
    description_text = description.get_attribute('content')
    if not 120 < len(description) < 160:
        print("description长度过长或是过短")
        return False
    description_text = lower(description_text)
    keyword = chrome.find_element(By.NAME, 'keywords')
    keyword_text = keyword.get_attribute('content')
    if not keyword_text in description_text:
        return False
    return True

def check_img(chrome):
    try:
        images = chrome.find_elements(By.TAG_NAME, 'img')
        for img in images:
            if img.get_attribute('src') == '':
                return False
        return True
    except Exception as e:
        print('获取图片失败：', e)
        return False

def check_paragraph(chrome):
    html_content = chrome.page_source
    soup = BeautifulSoup(html_content, "html.parser")
    paragraphs = soup.find_all("p")
    return len(paragraphs) > 1

def check_keywords_in_webpage(chrome):
    keyword = chrome.find_element(By.NAME, 'keywords')
    text_p = chrome.find_elements(By.TAG_NAME, 'p')
    text_h2 = chrome.find_elements(By.TAG_NAME, 'h2')
    text = ''
    text = text.join(i.text for i in text_p if i.text != '')
    text = text.join(i.text for i in text_h2 if i.text != '')
    if not keyword.text in text:
        return False
    return True

def is_readable(slug):
    # 判断是否只包含可读字符（字母、数字、-、中文）
    slug_decoded = urllib.parse.unquote(slug)  # 处理中文slug
    return bool(re.match(r'^[\w\-\u4e00-\u9fff]+$', slug_decoded))

def check_slug_access_identifier(chrome, url):
    keyword = chrome.find_element(By.NAME, 'keywords')
    keyword_text = keyword.get_attribute('content')
    keyword_text = set(keyword_text.split())
    url_list = extract_words_from_url(clean_text(url))
    stemmer = PorterStemmer()
    url_stems = set(stemmer.stem(word) for word in url_list)
    # 把关键词也stem处理
    keyword_stems = set(stemmer.stem(word.lower()) for word in keyword_text)
    if url_stems.isdisjoint(keyword_stems):
        print(f"slug{url}不包含关键词：{keyword_text}")
        return False
    if not is_readable(url.split('/')[-1]):
        print("slug包含不可读字符或者乱码")
        return False
    return True

def check_access_identifier(chrome, url):
    html_content = chrome.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    canonical_link = soup.find("link", rel="canonical")
    canonical_text = canonical_link.attrs['href']
    if canonical_text == url:
        return True
    return False

def analyze_headings(chrome, text):
    return analyze_headings_with_selenium(chrome, text)

def check_synonym(chrome):
    keyword = chrome.find_element(By.NAME, 'keywords')
    keyword = keyword.get_attribute('content')
    h2 = chrome.find_elements(By.TAG_NAME, 'h2')
    p = chrome.find_elements(By.TAG_NAME, 'p')
    h2text = [h.text for h in h2]
    stemmer = PorterStemmer()
    h2text = set(stemmer.stem(word) for word in h2text)
    # 把关键词也stem处理
    keyword_stems = set(stemmer.stem(word.lower()) for word in keyword.split())
    for i in h2text:
        i = clean_text(i)
        text = set(stemmer.stem(word) for word in i)
        if text.isdisjoint(keyword_stems):
            print(f"标题{i}不包含关键词：{keyword}")
            return False
    p = set(stemmer.stem(word.lower()) for word in p if word.text != None)
    if p.isdisjoint(keyword_stems):
            print(f"文章中不包含关键词：{keyword}")
            return False
    return True

class LinkChecker:
    def __init__(self, timeout=10, max_workers=10):
        self.timeout = timeout
        self.max_workers = max_workers
        self.valid_links = []
        self.invalid_links = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) LinkChecker/1.0'
        })

    def check_link(self, url):
        """检查单个链接"""
        try:
            start_time = time.time()
            # 发送HEAD请求减少数据传输
            response = self.session.head(
                url,
                allow_redirects=True,  # 跟踪重定向
                timeout=self.timeout,
                verify=True  # 验证SSL证书（设为False可跳过证书验证）
            )

            # 如果HEAD返回405（Method Not Allowed），改用GET请求
            if response.status_code == 405:
                response = self.session.get(
                    url,
                    allow_redirects=True,
                    timeout=self.timeout,
                    verify=True
                )

            status_code = response.status_code
            load_time = time.time() - start_time

            # 定义有效状态码范围
            if 200 <= status_code < 400:
                return {
                    'url': url,
                    'status': 'OK',
                    'status_code': status_code,
                    'load_time': f"{load_time:.2f}s",
                    'redirects': len(response.history)
                }
            else:
                return {
                    'url': url,
                    'status': 'ERROR',
                    'status_code': status_code,
                    'load_time': f"{load_time:.2f}s"
                }

        except requests.exceptions.RequestException as e:
            return {
                'url': url,
                'status': 'EXCEPTION',
                'error': str(e),
                'load_time': 'N/A'
            }

    def check_links(self, urls):
        """批量检查链接"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.check_link, url) for url in urls]
            results = [future.result() for future in futures]

        # 分类结果
        self.valid_links = [r for r in results if r['status'] == 'OK']
        self.invalid_links = [r for r in results if r['status'] != 'OK']
        return results

    def get_report(self):
        """生成格式化报告"""
        report = {
            'total': len(self.valid_links + self.invalid_links),
            'valid': len(self.valid_links),
            'invalid': len(self.invalid_links),
            'details': {
                'valid': self.valid_links,
                'invalid': self.invalid_links
            }
        }
        return report

def check_outside_chain(chrome):

    array = chrome.find_elements(By.TAG_NAME, 'a')
    test_urls = [i.get_attribute('href') for i in array]

    checker = LinkChecker(timeout=5, max_workers=5)
    results = checker.check_links(test_urls)
    report = checker.get_report()

    print(f"总链接数: {report['total']}")
    print(f"有效链接: {report['valid']}")
    print(f"无效链接: {report['invalid']}\n")

    # 打印详细结果
    print("有效链接详情:")
    for link in report['details']['valid']:
        print(
            f"{link['url']} | 状态码: {link['status_code']} | 加载时间: {link['load_time']} | 重定向次数: {link['redirects']}")

    print("\n无效链接详情:")
    for link in report['details']['invalid']:
        print(f"{link['url']} | 状态: {link['status']} | 错误: {link.get('error', f'''状态码 {link['status_code']}''')}")

    if len(report['details']['invalid']) > 0:
        return False
    return True
