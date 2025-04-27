from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import nltk
from nltk.stem import PorterStemmer
import re

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

def jumpProblem(url, chrome):
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

def keyWordsContrast(url, chrome):
    keyword =  chrome.find_element(By.NAME, 'keywords')
    title = chrome.find_element(By.TAG_NAME, 'title')

