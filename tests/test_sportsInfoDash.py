import pytest
import csv
import allure
from pages.sportsInfoDashTest import sportsInfo
from selenium.webdriver.edge.options import Options
from selenium import webdriver

# 基础指标
# title
# 是否包含关键词
# 是否有设置title标签
# 是否有设置h1标签的标题
# description
# 是否包含关键词
# 是否能表达当前网页的摘要
# 是否在120-160字符之间
# keywords
# 聚焦网页主要内容
# slug
# 网页唯一的可访问标识
# 足够语义化
# Canonical
# 可被搜索引擎引用的最佳URL（设置当前网页url即可，最权威）
# img
# 是否包含有图片嵌入（满足友好阅读体验）
# 重要指标
# 网页结构化
# 是否包含多级标签「h1, h2, h3...」
# 是否包含多个段落
# 关键词密度
# 各级标题中是否分布有「关键词、近义词」
# 各个段落中是否有多次出现「关键词、近义词」
# 外链
# 外链是否与当前页面具有相关性
# 外链是否能正常访问

def load_urls_from_csv(csv_path='../utils/sportsInfoURL.csv'):
    """从无表头的CSV读取URL"""
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)  # 不使用DictReader
        return [row[0] for row in reader if row]  # 提取每行第一个元素

@pytest.fixture(scope="module", params=load_urls_from_csv())
def url(request):
    return request.param

@pytest.fixture()
def chrome(url):
    options = Options()
    options.add_argument('--headless')  # 设置为无头模式
    options.add_argument('--disable-gpu')  # 禁用GPU加速（可选）
    options.add_argument('--window-size=1920x1080')
    edge = webdriver.Chrome(options=options)
    edge.get(url)
    yield edge
    edge.quit()

class Test:
    @allure.suite("体育信息")
    @allure.title("sprotsInfo: {url}")
    @allure.story("跳转问题")
    def test_JumpProblem(self, url, chrome):
        assert sportsInfo.jumpProblem(url, chrome)

    @allure.suite("体育信息")
    @allure.title("sprotsInfo: {url}")
    @allure.story("关键字对比")
    def test_JumpProblem(self, url, chrome):
        assert sportsInfo.keyWordsContrast(url, chrome)

