import time
import base64

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

# from volcenginesdkarkruntime import Ark

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
# client = Ark(
#     # 此为默认路径，您可根据业务所在地域进行配置
#     base_url="https://ark.cn-beijing.volces.com/api/v3",
#     # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
#     api_key='43e1ced5-7b01-4c04-913c-7ec9a47f8d3b'
# )

def image_to_base64(imagePath):
    ascllCode = requests.get(imagePath)
    if ascllCode.status_code == 200:
        baseCode = base64.b64encode(ascllCode.content)
        baseCode = baseCode.decode('utf-8')
    return baseCode

edge = webdriver.Edge()

edge.get('https://infohivehub.com/zh-CN')

articleArray = edge.find_elements(By.TAG_NAME, 'a')

ac = ActionChains(edge)

edge.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
ac.send_keys(Keys.PAGE_DOWN)

WebDriverWait(edge, 10).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))  # 或特定元素定位器
)


script = """
  const maxScroll = Math.max(
      document.body.scrollHeight, 
      document.documentElement.scrollHeight
  );
  window.scrollTo(0, maxScroll);
"""
edge.execute_script(script)
# 使用JavaScript直接滚动到底部
edge.execute_script("window.scrollTo(0, document.body.scrollHeight);")


httpDetailArray = []

for element in articleArray:
    if('detail' in element.get_attribute('href')):
        httpDetailArray.append(element.get_attribute('href'))

for element in httpDetailArray:
    edge.execute_script(f"window.open('{element}', '_blank');")

    WebDriverWait(edge, 10).until(
        EC.number_of_windows_to_be(2)  # 等待窗口数量变为2
    )
    windows = edge.window_handles
    edge.switch_to.window(windows[1])
    # try:
    #     video = edge.find_element(By.TAG_NAME, 'video')
    # except NoSuchElementException:
    #     print(f"该文章内没有引用视频: {element}")

    try:
        image = edge.find_element(By.TAG_NAME, 'img')
    except NoSuchElementException:
        print(f"该文章内没有引用图片: {element}")

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
    finally:
        # Non-streaming:
        # print("----- standard request -----")
        # completion = client.chat.completions.create(
        #     # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        #     model="deepseek-r1-distill-qwen-7b-250120",
        #     messages=[
        #         {"role": "system", "content": "你是人工智能助手."},
        #         {"role": "user", "content": f"你根据这篇文章1-100你打多少分\n{cleaned_text}"},
        #     ],
        # )
        # print(completion.choices[0].message.content)
        # print(f"该文章的分数：{score}")
        keywords = edge.find_elements(By.CLASS_NAME, 'bg-gray-700')
        keyword = [word.text for word in keywords]
        # matchKeywords.matchKeyword(cleaned_text, keywords)
        images = edge.find_elements(By.TAG_NAME, 'img')

        imagePath = []

        [imagePath.append(image.get_attribute('src')) for image in images]

        imageArray = []

        [imageArray.append(image_to_base64(image)) for image in imagePath]
        param = {
            "model": "llava",
            "prompt":  f"我给你一篇文章{cleaned_text}\n"
                       f"请你回答我下面三个问题："
                       f"1.你觉得这篇文章的内容和{keyword}这几个关键字相关吗？"
                       f"2.我提供的图片和文章相关吗？"
                       f"3.你觉得这篇文章1-100你打多少分？",
            "stream": False,
            "images": imageArray
        }

        response = requests.request(
            'POST', 'http://localhost:11434/api/generate', json=param
        )

        jsondata = json.loads(response.text)
        print(jsondata['response'])
        windows = edge.window_handles
        edge.close()
        edge.switch_to.window(windows[0])
        break
