from io import BytesIO

import requests
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoFeatureExtractor, AutoModelForImageClassification,AutoProcessor,BlipProcessor,BlipForConditionalGeneration,CLIPProcessor,CLIPModel
from PIL import Image
import torch
import json
from selenium import webdriver

# 判断文章是否包含违禁词
def JudgeLllegalWords(text):
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased", num_labels=2)

    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    predicted = torch.argmax(outputs.logits, dim=1).item()
    return predicted

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
    # 这里调用 nsfw_model(image_tensor) 返回标签/概率
    # 加载模型
    processor = AutoProcessor.from_pretrained("Falconsai/nsfw_image_detection")
    model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")

    # 加载图片
    # 获取图片内容（留在内存中）
    to_pil = T.ToPILImage()
    image = to_pil(image_tensor.squeeze(0)).convert("RGB")

    # 使用 PIL 打开图片（不保存本地）
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)

    # 输出标签和概率
    labels = model.config.id2label
    arr = []
    for i, p in enumerate(probs[0]):
        arr.append(f"{labels[i]}: {p.item():.2%}")
        print(f"{labels[i]}: {p.item():.2%}")

    return arr

def detect_horror(image_tensor):
    response = requests.get(image_tensor, allow_redirects=True)
    params = {
        'url': response.url,
        'models': 'gore-2.0',
        'api_user': '285381362',
        'api_secret': 'yWPvsrEKjA8SuYynXGbEbvmEW5gAhhNc'
    }
    r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
    response = json.loads(r.text)
    gore = response["gore"]
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

# 主函数
def run_all(image_path_or_url):
    image = load_image(image_path_or_url)

    # 转为tensor（供其他模型使用）
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor()
    ])
    img_tensor = transform(image).unsqueeze(0)

    nsfw_result = detect_nsfw(img_tensor)
    horror_result = detect_horror(image_path_or_url)
    anomaly_result = detect_anomaly(image)

    print("NSFW 检测:", nsfw_result)
    print("恐怖图检测:", horror_result)
    print("AI 异常检测:", anomaly_result)

# 判断文章里面的图片是否违规
def judgeLllgalImage(imageArray):
    for image in imageArray:
        run_all(image)

def judgeNSFWImage(imageArray):
    for image in imageArray:
       img_tensor = run_all(image)
       nsfw_result = detect_nsfw(img_tensor)
       for nsfw in nsfw_result:
           key, value = nsfw.split(':')
           if key == 'normal' and value > 50:
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
def analyze_headings_with_selenium(edge):
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
        return True
    finally:
        print()