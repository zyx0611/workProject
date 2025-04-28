from selenium.webdriver.common.by import By
import nltk
from nltk.stem import PorterStemmer
import re
from bs4 import BeautifulSoup
from soupsieve.util import lower

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

