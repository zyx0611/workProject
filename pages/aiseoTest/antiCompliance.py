from serpapi import GoogleSearch
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import difflib
API_KEY = "cffb95c1bfd214f02a230d7c564892c3ad4b5836fcfb7fefdf2bf7361062b794"

# 伪原创检测
def check_duplicate_by_search(text, threshold=0.5):
    sentences = [s.strip() for s in text.split("。") if len(s.strip()) > 5]
    hit_count = 0

    for sent in sentences:
        params = {
            "engine": "google",
            "q": f'"{sent}"',  # 使用引号精确匹配句子
            "api_key": API_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results and len(results["organic_results"]) > 0:
            hit_count += 1
            print(f"[重复] 句子：{sent}")
        else:
            print(f"[原创] 句子：{sent}")

        time.sleep(1.5)  # 防止超速请求

    hit_ratio = hit_count / len(sentences)
    print(f"\n疑似重复率：{hit_ratio:.2%}")

    print("\n结果：", "疑似抄袭" if hit_ratio > threshold else "原创内容") # 超过50%就认定为重复
    if hit_ratio > threshold:
        return False
    else:
        return True

# 重定向欺骗
def Redirect_deception(edge):
    pageSource = edge.page_source

    # 检查是否存在 meta refresh 标签
    if '<meta http-equiv="refresh"' in pageSource:
        print("页面包含 Meta Refresh 跳转")
        return False
    else:
        print("没有找到 Meta Refresh 跳转")

    # 检查页面中是否存在 `window.location.href` 或类似重定向代码
    scripts = edge.find_elements(By.TAG_NAME, "script")

    for script in scripts:
        if "window.location.href" in script.get_attribute("innerHTML"):
            print("页面包含 JavaScript 重定向")
            return False
        else:
            print("没有找到 JavaScript 重定向")
    return True

# 外链作弊
# 你的 IPQS API Key
IPQS_API_KEY = "uRjeBGd9dFWtBmxnNU78k0k8v7HenuaF"  # 替换为你自己的

def check_link_with_ipqs(link):
    """
    使用 IPQS 检查链接是否为可疑网站
    """
    api_url = f"https://ipqualityscore.com/api/json/url/{IPQS_API_KEY}/{link}"
    try:
        response = requests.get(api_url)
        data = response.json()
        return {
            "is_suspicious": data.get("suspicious", False),
            "unsafe": data.get("unsafe", False),
            "category": data.get("category", "unknown"),
            "domain_rank": data.get("domain_rank", 0)
        }
    except Exception as e:
        return {
            "is_suspicious": False,
            "unsafe": False,
            "category": "error",
            "domain_rank": 0
        }

def analyze_links(edge):
    """
    分析网页中所有的 a 标签链接，判断 nofollow 状态并检测链接质量
    """

    a_tags = edge.find_elements(By.TAG_NAME, 'a')
    results = []

    for a in a_tags:
        href = a.get_attribute('href')
        rel = a.get_attribute('rel') or ''
        anchor_text = a.text.strip()
        is_nofollow = 'nofollow' in rel.lower()

        if href and href.startswith('http'):
            quality_check = check_link_with_ipqs(href)
            results.append({
                '链接': href,
                '锚文本': anchor_text,
                'nofollow': is_nofollow,
                '可疑': quality_check['is_suspicious'],
                '不安全': quality_check['unsafe'],
                '分类': quality_check['category'],
                '域名排名': quality_check['domain_rank']
            })

    edge.quit()
    return results

# 定位正文元素（根据实际情况调整选择器）
# body_element = edge.find_element(By.CLASS_NAME, "markdown-content")

# 提取并清理文本
# raw_text = body_element.get_attribute("innerText")
# cleaned_text = raw_text.replace("\n", " ")  # 合并换行符

def get_page_content(url, user_agent):
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers, timeout=10)
    return response.text

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 提取纯文本内容（不含标签）
    return soup.get_text(separator=' ', strip=True)

def check_cloaking(url):
    user_agent_bot = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    user_agent_user = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

    html_bot = get_page_content(url, user_agent_bot)
    html_user = get_page_content(url, user_agent_user)

    text_bot = extract_text(html_bot)
    text_user = extract_text(html_user)

    # 使用 difflib 计算差异相似度
    similarity = difflib.SequenceMatcher(None, text_bot, text_user).ratio()

    print(f"页面文本相似度：{similarity:.2f}")
    if similarity < 0.8:
        print("⚠️ 可能存在 cloaking 欺骗行为（搜索引擎与用户看到内容差异大）")
        return False
    else:
        print("✅ 页面内容一致，无明显 cloaking")
        return True

import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import jieba
import re

def fetch_text(url):
    headers = {'User-Agent': "Mozilla/5.0 Chrome/120"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def tokenize_mixed(text):
    chinese_words = jieba.lcut(text)
    english_words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    tokens = chinese_words + english_words
    tokens = [w.lower() for w in tokens if len(w.strip()) > 1]
    return tokens

def analyze_keyword_stuffing_with_density(url, tfidf_threshold=0.15, density_threshold=5.0):
    text = fetch_text(url)
    tokens = tokenize_mixed(text)
    total_words = len(tokens)
    word_counts = Counter(tokens)

    # 自定义 tokenizer 给 TfidfVectorizer
    def dummy_tokenizer(doc):
        return tokenize_mixed(doc)

    vectorizer = TfidfVectorizer(tokenizer=dummy_tokenizer, stop_words=None, max_features=100)
    tfidf_matrix = vectorizer.fit_transform([text])
    tfidf_values = tfidf_matrix.toarray()[0]
    tfidf_words = vectorizer.get_feature_names_out()

    print("🔍 Top 10 TF-IDF 关键词 + 密度：")
    for i in tfidf_values.argsort()[::-1][:10]:
        word = tfidf_words[i]
        tfidf_score = tfidf_values[i]
        freq = word_counts.get(word, 0)
        density = round((freq / total_words) * 100, 2)
        print(f"{word:<15} TF-IDF: {tfidf_score:.4f}  | 密度: {density:.2f}%  | 出现次数: {freq}")

    top_word = tfidf_words[tfidf_values.argmax()]
    top_score = tfidf_values.max()
    total_score = tfidf_values.sum()

    warnings = []
    if top_score / total_score > tfidf_threshold:
        warnings.append(f"⚠️ TF-IDF 占比过高：'{top_word}'")

    for word in tfidf_words:
        freq = word_counts.get(word, 0)
        density = (freq / total_words) * 100
        if density > density_threshold:
            warnings.append(f"⚠️ 关键词密度过高：'{word}' 密度={density:.2f}%")

    if warnings:
        print("\n".join(warnings))
        print("🚨 可能存在关键词堆叠行为！")
        return False
    else:
        print("✅ 未发现异常关键词堆叠。")
        return True



