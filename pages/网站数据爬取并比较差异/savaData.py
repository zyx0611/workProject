import json

from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import date

from selenium import webdriver
import time

from selenium.webdriver.support.wait import WebDriverWait

edge = webdriver.Edge()

edge.get('http://13.251.42.112:8800/admin/#/admin/xhs_app/crawlmedevice/')
# password  username el-button el-button--primary

edge.find_element(By.NAME, 'username').send_keys('ml_test')

edge.find_element(By.NAME, 'password').send_keys('jscDyKgpLe')

edge.find_element(By.CLASS_NAME, 'el-button').click()

edge.get('http://13.251.42.112:8800/admin/#/admin/xhs_app/crawlmedevice/')

handle = edge.window_handles

edge.switch_to.window(handle[-1])


wait = WebDriverWait(edge, 10)
infoButton = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='200账号详情']"))
    # edge.find_element(By.XPATH, "//span[text()='200账号详情']")
)
# infoButton.click()
ActionChains(edge).move_to_element(infoButton).click(infoButton).perform()

edge.switch_to.default_content()

# tbody = WebDriverWait(edge, 100).until(
#     EC.element_to_be_clickable((By.TAG_NAME, 'tbody'))
# )
# print('tbody')
#
#
# tr = WebDriverWait(edge, 100).until(
#     EC.element_to_be_clickable((By.TAG_NAME, 'tr'))
# )
# print('tr')
#
# td = WebDriverWait(edge, 100).until(
#     EC.element_to_be_clickable((By.TAG_NAME, 'td'))
# )
# print('td')

iframe = edge.find_element(By.TAG_NAME, "iframe")
edge.switch_to.frame(iframe)

page = edge.find_element(By.CLASS_NAME, 'el-pager')

print(page)
pageNumber = len(list(page.text))
current_page = 1
edge.switch_to.default_content()

textData = []
iframe = edge.find_element(By.TAG_NAME, "iframe")
edge.switch_to.frame(iframe)
table = edge.find_element(By.TAG_NAME, 'table')
header_row = table.find_element(By.TAG_NAME, 'tr')
str = header_row.text

# 3. 提取表头文本
# header_texts = [th.text.strip() for th in header_row.text]
header_texts = str.split("\n")
textData.append(header_texts)
edge.switch_to.default_content()

while current_page <= pageNumber:
    iframe = edge.find_element(By.TAG_NAME, "iframe")
    edge.switch_to.frame(iframe)
    table = edge.find_element(By.TAG_NAME, 'table')
    # header_row = table.find_element(By.TAG_NAME, 'tr')
    # str = header_row.text

    # 3. 提取表头文本
    # header_texts = [th.text.strip() for th in header_row.text]
    # header_texts = str.split("\n")
    # textData.append(header_texts)

    rows = table.find_elements(By.TAG_NAME, "tr")  # 获取所有行
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        tdData = []# 获取单元格
        for index,col in enumerate(cols):
            if index != 0:
                tdData.append(col.text)
        if len(tdData) != 0:
            textData.append(tdData)

    try:
        next_button = edge.find_element(By.CLASS_NAME, 'btn-next')
        next_button.click()
        time.sleep(3)
        current_page += 1
        # 返回主文档
        edge.switch_to.default_content()
    except NoSuchElementException:
        print("没有更多页面了")
        break

with open(f"{date.today()}用户数据.csv", 'w', newline='', encoding='utf-8') as f:
    for i in textData:
        for element in i:
            f.write(f'{element},')
        f.write(f'\n')