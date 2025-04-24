import base64

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import requests
import json
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from sentence_transformers import SentenceTransformer, util
from typing import List

def image_to_base64(imagePath):
    ascllCode = requests.get(imagePath)
    if ascllCode.status_code == 200:
        baseCode = base64.b64encode(ascllCode.content)
        baseCode = baseCode.decode('utf-8')
    return baseCode

def checkImage(edge):
    try:
        image = edge.find_element(By.TAG_NAME, 'img')
        if image is not None:
            return True
    except NoSuchElementException:
        print("该文章内没有引用图片")
        return False

def extractImageTextKeyWord(edge):
    try:
        image = edge.find_elements(By.TAG_NAME, 'img')
    except NoSuchElementException:
        print(f"该文章内没有引用图片")

    try:
        # 定位正文元素（根据实际情况调整选择器）
        body_element = edge.find_element(By.CLASS_NAME, "markdown-content")

        # 提取并清理文本
        raw_text = body_element.get_attribute("innerText")
        cleaned_text = raw_text.replace("\n", " ")  # 合并换行符

        # 计算长度指标
        word_count = len(cleaned_text)
        char_count = len(cleaned_text)
        paragraph_count = len(body_element.find_elements(By.TAG_NAME, "p"))
        print(f"字数: {word_count}, 字符数: {char_count}, 段落数: {paragraph_count}")
    except Exception as e:
        print("检测正文长度失败:", e)
    keywords = edge.find_elements(By.CLASS_NAME, 'bg-gray-700')
    keyword = [word.text for word in keywords]
    return {
        "keyword": keyword,
        "text": cleaned_text,
        "images": image
    }

def invokingLlama(param):

    response = requests.request(
        'POST', 'http://localhost:11434/api/generate', json=param
    )
    if response.status_code == 200:
        jsondata = json.loads(response.text)
        return jsondata['response']
    else:
        print(f'llama模型调用失败！{response.text}')
    return False


def checkTextAndKeyword(edge):
    element = extractImageTextKeyWord(edge)
    cleaned_text = element["text"]
    keyword = element["keyword"]
    param = {
        "model": "llava",
        "prompt": f"我给你一篇文章{cleaned_text}\n你觉得这篇文章的内容和{keyword}这几个关键字相关吗，相关就给我说True，不相关就说False",
        "stream": False,
    }
    data = invokingLlama(param)
    return data

# 加载模型（建议外部只加载一次）
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def checkTextAndImage(text: str, image_urls: List[str], threshold: float = 0.4) -> bool:
    """
    检查图像与文本是否语义一致。
    参数:
        text: 文章正文或摘要
        image_urls: 图片链接列表
        threshold: 相似度阈值（低于此值认为不一致）
    返回:
        如果任意一张图与文本相似度高于阈值，则返回 True，否则 False。
    """
    text_embedding = sbert_model.encode(text, convert_to_tensor=True)

    for url in image_urls:
        try:
            img = Image.open(requests.get(url, stream=True).raw).convert("RGB")
            inputs = blip_processor(images=img, return_tensors="pt")
            out = blip_model.generate(**inputs)
            caption = blip_processor.decode(out[0], skip_special_tokens=True)

            print(f"[图像描述] {url} -> {caption}")
            caption_embedding = sbert_model.encode(caption, convert_to_tensor=True)
            similarity = util.cos_sim(text_embedding, caption_embedding).item()
            print(f"→ 相似度: {similarity:.4f}")

            if similarity <= threshold:
                return False  # 有一张不合规就全都不合规
        except Exception as e:
            print(f"处理图像失败: {url}, 错误: {e}")

    return True