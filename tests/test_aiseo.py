import csv

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

from pages.aiseoTest import aiseoTest, antiCompliance, compliance
from selenium import webdriver
import allure
import subprocess

# @pytest.fixture(scope="session", autouse=True)
# def generate_csv_data():
#     subprocess.run(["python", "/Users/edy/PycharmProjects/workProject/getYesterdayURL.py"])

# ---------------------------
# 工具函数：数据加载与校验
# ---------------------------
# def load_urls_from_csv(csv_path='yesterdayURL.csv'):
def load_urls_from_csv(csv_path='Utils/yesterdayURL.csv'):
    """从无表头的CSV读取URL"""
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)  # 不使用DictReader
        return [row[0] for row in reader if row]  # 提取每行第一个元素

@pytest.fixture(scope="module", params=load_urls_from_csv())
def url(request):
    return request.param

@pytest.fixture()
def edge(url):
    options = Options()
    options.add_argument('--headless')  # 设置为无头模式
    options.add_argument('--disable-gpu')  # 禁用GPU加速（可选）
    options.add_argument('--window-size=1920x1080')
    edge = webdriver.Edge(options=options)
    edge.get(url)
    return edge


@pytest.fixture()
def webdriverStater(edge):
    yield edge
    edge.quit()


@pytest.fixture()
def webdriverStaterGetText(edge):
    # 定位正文元素（根据实际情况调整选择器）
    body_element = edge.find_element(By.CLASS_NAME, "markdown-content")

    # 提取并清理文本
    raw_text = body_element.get_attribute("innerText")
    cleaned_text = raw_text.replace("\n", " ")
    yield cleaned_text
    edge.quit()  # 合并换行符

@pytest.fixture()
def webdriverStaterGetImage(edge):
    images = edge.find_elements(By.TAG_NAME, 'img')
    imagePath = []
    [imagePath.append(image.get_attribute('src')) for image in images]
    yield imagePath
    edge.quit()

@pytest.fixture()
def webdriverStaterGetKeyword(edge):
    keywords = edge.find_elements(By.CLASS_NAME, 'bg-gray-700')
    keyword = [word.text for word in keywords]
    yield keyword
    edge.quit()

class TestAiseo:
    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("测试图片")
    def testCheckImage(self, webdriverStater, url):
        print("测试图片")
        allure.dynamic.feature(url)
        assert aiseoTest.checkImage(webdriverStater)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("测试文章和关键字的关系")
    def testCheckTextAndKeyword(self, webdriverStater, url):
        print('测试文章和关键字的关系')
        allure.dynamic.feature(url)
        assert aiseoTest.checkTextAndKeyword(webdriverStater)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("测试文章和图片的关系")
    def testCheckTextAndImage(self, webdriverStaterGetText, url,webdriverStaterGetImage):
        print('测试文章和图片的关系')
        allure.dynamic.feature(url)
        assert aiseoTest.checkTextAndImage(webdriverStaterGetText,webdriverStaterGetImage)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断文章是否包含违禁词")
    def testJudgeLllegalWords(self, webdriverStaterGetText, url):
        print("判断文章是否包含违禁词")
        allure.dynamic.feature(url)
        assert compliance.JudgeLllegalWords(webdriverStaterGetText)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断图片状态码")
    def testImageCode(self, webdriverStaterGetImage, url):
        print("判断图片状态码")
        allure.dynamic.feature(url)
        assert compliance.checkImage(webdriverStaterGetImage)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断图片是否包含黄色内容")
    def testjudgeNSFWImage(self, webdriverStaterGetImage, url):
        print("判断图片是否包含黄色内容")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        assert compliance.judgeNSFWImage(webdriverStaterGetImage)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断图片是否包含恐怖内容")
    def testHorrorImage(self, webdriverStaterGetImage, url):
        print("判断图片是否包含恐怖内容")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        assert compliance.judgeHorrorImage(webdriverStaterGetImage)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断图片是否是AI错图")
    def testAnomalyImage(self, webdriverStaterGetImage, url):
        print("判断图片是否是AI错图")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        assert compliance.judgeAnomalyImage(webdriverStaterGetImage)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断网页结构是否正常")
    def testAnalyzeHeadingsWithSelenium(self,url, webdriverStater,webdriverStaterGetText):
        print("判断网页结构是否正常")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        assert compliance.analyze_headings_with_selenium(webdriverStater, webdriverStaterGetText)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断关键字密度")
    def testMatchKeyword(self, webdriverStaterGetText, url, webdriverStaterGetKeyword):
        print("判断关键字密度")
        assert compliance.matchKeyword(webdriverStaterGetText, webdriverStaterGetKeyword)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断文章是否伪原创")
    def testDuplicateBySearch(self, webdriverStaterGetText, url):
        print("判断文章是否伪原创")
        allure.dynamic.feature(url)
        # assert antiCompliance.check_duplicate_by_search(webdriverStaterGetText)
        assert antiCompliance.is_plagiarized(webdriverStaterGetText)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断重定向欺骗")
    def testRedirectDeception(self, webdriverStater, url):
        print("判断重定向欺骗")
        allure.dynamic.feature(url)
        assert antiCompliance.Redirect_deception(webdriverStater)
        webdriverStater.quit()

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断外链作弊")
    def testLinkWithIpqs(self, webdriverStater, url):
        print("判断外链作弊")
        allure.dynamic.feature(url)
        assert antiCompliance.analyze_links(webdriverStater)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("判断cloaking欺骗")
    def testCheckCloaking(self, webdriverStater, url):
        print("判断cloaking欺骗")
        allure.dynamic.feature(url)
        assert antiCompliance.check_cloaking(webdriverStater.current_url)

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("测试关键词堆叠")
    def testAnalyzeKeywordStuffingWithDensity(self, webdriverStater, url):
        print("测试关键词堆叠")
        allure.dynamic.feature(url)
        assert antiCompliance.analyze_keyword_stuffing_with_density(webdriverStater.current_url)


if __name__ == '__main__':
    pytest.main()