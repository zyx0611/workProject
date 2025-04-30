import csv
import requests
from PIL import Image
import json
from langdetect import detect
import jieba
from bs4 import BeautifulSoup
import time

class APIRequester:
    def __init__(self):
        with open('../utils/sightengineApikey.csv', 'r') as f:
            reader = csv.reader(f)
            api_keys = [row[0] for row in reader if row]
        self.api_keys = api_keys
        self.index = 0

    def get_current_key(self):
        if self.index >= len(self.api_keys):
            return None
        return self.api_keys[self.index]

    def switch_key(self):
        self.index += 1

    def make_request(self, url, params=None, headers=None):
        retries = 0
        max_retries = len(self.api_keys)
        while retries < max_retries and self.index < len(self.api_keys):
            api_key = self.get_current_key()
            print(f"使用apikey: {api_key}")

            # 更新header加上apikey（根据你的接口调整）
            if headers is None:
                headers = {}
            headers['Authorization'] = f"Bearer {api_key}"

            api_key_arr = api_key.split('-')
            params['api_user'] = api_key_arr[0]
            params['api_secret'] = api_key_arr[1]

            try:
                if 'text' in params :
                    response = requests.get(url, data=params, headers=headers, timeout=10)
                else :
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"⚠️ 接口返回错误 {response.status_code}，尝试更换API Key...")
                    self.switch_key()
                    retries += 1
                    time.sleep(1)  # 防止频繁请求被封
            except Exception as e:
                print(f"❌ 请求异常: {e}，尝试更换API Key...")
                self.switch_key()
                retries += 1
                time.sleep(1)

        raise Exception("❌ 所有API Key都不可用或重试失败")

def detect_language_langdetect(text):
    try:
        lang = detect(text)
        return lang  # 'zh-cn' 表示中文，'en' 表示英文
    except:
        return "Unknown"

# 加载外部违规词库
def load_banned_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        banned_words = f.read().splitlines()
    return banned_words

# 使用结巴进行分词检测
def detect_banned_words(text, banned_words):
    words = jieba.lcut(text)
    found_words = [word for word in words if word in banned_words]

    if found_words:
        return False, found_words
    else:
        return True, []

# 判断文章是否包含违禁词
def JudgeLllegalWords(text):
    langdetect = detect_language_langdetect(text)
    if langdetect == 'zh-cn':
        # 加载违规词库
        banned_words = load_banned_words('../utils/色情类.txt')
        # 检测是否有违禁词
        is_banned, banned_found = detect_banned_words(text, banned_words)
        print("违规词：", banned_found)
        return is_banned
    else:
        categories = 'profanity,personal,link,drug,weapon,spam,content-trade,money-transaction,extremism,violence,self-harm,medical'
        data = {
            'text': text,
            'mode': 'rules',
            'lang': 'en',
            'categories': categories,
            'api_user': '',
            'api_secret': ''
        }
        try:
            url = 'https://api.sightengine.com/1.0/text/check.json'
            requester = APIRequester()
            result = requester.make_request(url, data)
            output = json.loads(result.text)
            available = categories.split(',')
            for ava in available:
                element = output.get(ava, {})
                matches = element.get('matches', [])
                if len(matches) > 0:
                    for match in matches:
                        if match.get('intensity') != 'low':
                            return False
            return True
        except Exception as e:
            print("请求报错：", e)

import torchvision.transforms as T
import numpy as np

# 下载并加载图片
def load_image(url_or_path):
    response = requests.get(url_or_path, timeout=5)
    if response.status_code != 200:
        print(f"图片状态码有问题：{response.status_code}")
    else :
        print("图片状态码没问题")
    if url_or_path.startswith("http"):
        image = Image.open(requests.get(url_or_path, stream=True).raw).convert("RGB")
    else:
        image = Image.open(url_or_path).convert("RGB")
    return image


def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        return response.url
    except Exception as e:
        return str(e)

def checkImage(urlArr):
    for url in urlArr:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"图片状态码有问题：{response.status_code}")
            return False
        else:
            print("图片状态码没问题")
    return True

# 模拟 NSFW 和 horror 判断（需调用你训练好的模型）
def detect_nsfw(image_tensor):
    params = {
        'url': image_tensor,
        'models': 'nudity-2.1',
        'api_user': '285381362',
        'api_secret': 'yWPvsrEKjA8SuYynXGbEbvmEW5gAhhNc'
    }
    url = 'https://api.sightengine.com/1.0/check.json'
    requester = APIRequester()

    try:
        # r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
        result = requester.make_request(url, params)
        nudity = result.get("nudity", {})

        # 可以选择关注的字段（越靠前越严重）
        flags = [
            "sexual_activity",
            "sexual_display",
            "erotica",
            "very_suggestive",
            "suggestive",
            "mildly_suggestive"
        ]

        for flag in flags:
            if nudity.get(flag, 0) > 0.5:
                print(f'该图片{flag}指数过高！')
                return True  # 这张图被认为有黄内容

        return False  # 安全
    except Exception as e:
        print("请求报错：", e)

def detect_horror(image_tensor):
    requester = APIRequester()
    response = requests.get(image_tensor, allow_redirects=True)
    url = 'https://api.sightengine.com/1.0/check.json'
    params = {
        'url': response.url,
        'models': 'gore-2.0',
        'api_user': '',
        'api_secret': ''
    }
    # r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
    result = requester.make_request(url, params)
    gore = result["gore"]
    if (gore["prob"] > 0.001) :
        return True
    else:
        return False


# AI 错图检测（基础版）
def detect_anomaly(image):
    import cv2
    import mediapipe as mp
    np_img = np.array(image)
    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR))
        if not results.pose_landmarks:
            return "No human detected"
        keypoints = results.pose_landmarks.landmark
        if len(keypoints) > 33:  # mediapipe 正常是33点，更多可能是重复或错误识别
            return "Possibly abnormal (extra limbs)"
    return "Normal"

def judgeNSFWImage(imageArray):
    for image in imageArray:
       image = get_final_url(image)
       nsfw_result = detect_nsfw(image)
       if nsfw_result:
           return False
    return True

def judgeHorrorImage(imageArray):
    for image in imageArray:
        if detect_horror(image):
            return False
    return True

def judgeAnomalyImage(imageArray):
    for image in imageArray:
        image = load_image(image)
        if detect_anomaly(image) == 'Possibly abnormal (extra limbs)':
            return False
    return True


# 关键词出现的次数与密度

import spacy
from spacy.matcher import PhraseMatcher

# 加载 spaCy 的多语言模型，能处理中英文混合文本
nlp = spacy.load("xx_ent_wiki_sm")  # 小型多语言模型，适合中文+英文混合


def matchKeyword(text, keywords):
    doc = nlp(text)

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  # 不区分大小写
    patterns = [nlp.make_doc(kw.lower()) for kw in keywords]
    matcher.add("KeywordList", patterns)

    # 统计匹配
    matches = matcher(doc)
    match_count = {}
    total_words = len([token for token in doc if token.is_alpha])

    for match_id, start, end in matches:
        phrase = doc[start:end].text.lower()
        match_count[phrase] = match_count.get(phrase, 0) + 1

    # 计算密度
    density = {}
    for kw in match_count:
        density[kw] = round((match_count[kw] / total_words) * 100, 2)

    print("关键字密度：", density)
    print("关键字出现次数：", match_count)

    # 判断所有关键词是否都出现（忽略大小写）
    normalized_keywords = set([kw.lower() for kw in keywords])
    matched_keywords = set(match_count.keys())

    if normalized_keywords.issubset(matched_keywords):
        print("✅ 所有关键字都出现了")
        return True
    else:
        missing = normalized_keywords - matched_keywords
        print("⚠️ 有关键字没有出现：", missing)
        return False


# 查看H结构是否正常
from selenium.webdriver.common.by import By
def analyze_headings_with_selenium(edge, cleaned_text):
    try:
        headings = []
        for level in range(1, 7):
            tags = edge.find_elements(By.TAG_NAME, f'h{level}')
            for tag in tags:
                text = tag.text.strip()
                if text:
                    headings.append((f'h{level}', text))

        h1_count = sum(1 for tag, _ in headings if tag == 'h1')
        if h1_count == 0:
            print("❌ 缺少 <h1> 标签")
            return False
        elif h1_count > 1:
            print(f"⚠️ 存在多个 <h1> 标签（{h1_count} 个）")
        else:
            print("✅ 正常包含一个 <h1> 标签")

        print("\n📚 页面 H 标签结构：")
        last_level = 0
        for tag, text in headings:
            level = int(tag[1])
            if last_level and level > last_level + 1:
                print(f"⚠️ 跳级结构：{tag.upper()} 在 {last_level} 后出现")
                return False
            print(f"  {tag.upper()}: {text}")
            last_level = level
    finally:
        soup = BeautifulSoup(cleaned_text, "html.parser")
        title_tag = soup.find("title")
        title_text = title_tag.text.strip() if title_tag else ""
        length = len(title_text)
        print(f"\n[Meta Title] 长度: {length} 字符，内容：{title_text}")
        if not (title_tag and 10 <= length <= 60):
            return False
        desc_tag = soup.find("meta", attrs={"name": "description"})
        desc = desc_tag.get("content", "") if desc_tag else ""
        length = len(desc.strip())
        print(f"\n[Meta Description] 长度: {length} 字符，内容：{desc.strip()}")
        if not (desc_tag is not None and 50 <= length <= 160):
            return False
        return True