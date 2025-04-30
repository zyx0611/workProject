import pytest
import csv
import allure
from pages.sportsInfoDashTest import sportsInfo
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By


def load_urls_from_csv(csv_path='../utils/sportsInfoURL.csv'):
    """从无表头的CSV读取URL"""
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)  # 不使用DictReader
        return [row[0] for row in reader if row]  # 提取每行第一个元素

@pytest.fixture(scope="module", params=load_urls_from_csv())
def url(request):
    return request.param

@pytest.fixture()
def webdriverStaterGetText(chrome):
    # 定位正文元素（根据实际情况调整选择器）
    body_element = chrome.find_element(By.CLASS_NAME, "markdown-content")

    # 提取并清理文本
    raw_text = body_element.get_attribute("innerText")
    cleaned_text = raw_text.replace("\n", " ")
    yield cleaned_text
    chrome.quit()  # 合并换行符

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
    @allure.title("sports_info: {url}")
    @allure.story("跳转问题")
    def test_jump_problem(self, url, chrome):
        assert sportsInfo.jump_problem(url, chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("关键字对比")
    def test_keywords_contrast(self, url, chrome):
        assert sportsInfo.keywords_contrast_and_title(url, chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("h1标签")
    def test_h1(self, url, chrome):
        assert sportsInfo.find_h1(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("description是否包含关键词")
    def test_description_keywords(self, url, chrome):
        assert sportsInfo.description_keywords(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("description是否包含关键词")
    def test_description_keywords(self, url, chrome):
        assert sportsInfo.description_keywords(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("是否包含有图片嵌入")
    def test_check_img(self, url, chrome):
        assert sportsInfo.check_img(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("检查文章是否包含多个段落")
    def test_check_paragraph(self, url, chrome):
        assert sportsInfo.check_paragraph(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("keywords聚焦网页主要内容")
    def test_keywords_in_webpage(self, url, chrome):
        assert sportsInfo.check_keywords_in_webpage(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("slug网页唯一的可访问标识")
    def test_slug_access_identifier(self, url, chrome):
        assert sportsInfo.check_slug_access_identifier(chrome, url)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("Canonical可被搜索引擎引用的最佳URL")
    def test_access_identifier(self, url, chrome):
        assert sportsInfo.check_access_identifier(chrome, url)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("是否包含多级标签")
    def test_analyze_headings(self, url, chrome, webdriverStaterGetText):
        assert sportsInfo.analyze_headings(chrome, webdriverStaterGetText)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("各级标题正文中是否分布有关键词、近义词")
    def test_check_synonym(self, url, chrome):
        assert sportsInfo.check_synonym(chrome)

    @allure.suite("体育信息")
    @allure.title("sports_info: {url}")
    @allure.story("外链是否能正常访问")
    def test_check_outside_chain(self, url, chrome):
        assert sportsInfo.check_outside_chain(chrome)