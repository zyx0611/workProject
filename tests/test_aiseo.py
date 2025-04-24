import csv

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

from pages.aiseoTest import aiseoTest, antiCompliance, compliance
from selenium import webdriver
import subprocess

# @pytest.fixture(scope="session", autouse=True)
# def generate_csv_data():
#     subprocess.run(["python", "/Users/edy/PycharmProjects/workProject/getYesterdayURL.py"])

# ---------------------------
# 工具函数：数据加载与校验
# ---------------------------
def load_urls_from_csv(csv_path='yesterdayURL.csv'):
# def load_urls_from_csv(csv_path='../Utils/yesterdayURL.csv'):
    """从无表头的CSV读取URL"""
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)  # 不使用DictReader
        return [row[0] for row in reader if row]  # 提取每行第一个元素

# @pytest.fixture(scope="module", params=load_urls_from_csv())
# def url(request):
#     return request.param

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
    def testCheckImage(self, webdriverStater):
        print("测试图片")
        assert aiseoTest.checkImage(webdriverStater)

    def testCheckTextAndKeyword(self, webdriverStater):
        print('测试文章和关键字的关系')
        assert aiseoTest.checkTextAndKeyword(webdriverStater)

    def testCheckTextAndImage(self, webdriverStaterGetText,webdriverStaterGetImage):
        print('测试文章和图片的关系')
        assert aiseoTest.checkTextAndImage(webdriverStaterGetText,webdriverStaterGetImage)

    def testJudgeLllegalWords(self, webdriverStaterGetText):
        print("判断文章是否包含违禁词")
        assert compliance.JudgeLllegalWords(webdriverStaterGetText)

    def testImageCode(self, webdriverStaterGetImage):
        print("判断图片状态码")
        assert compliance.checkImage(webdriverStaterGetImage)

    def testjudgeNSFWImage(self, webdriverStaterGetImage):
        print("判断图片是否包含黄色内容")
        assert compliance.judgeNSFWImage(webdriverStaterGetImage)

    def testHorrorImage(self, webdriverStaterGetImage):
        print("判断图片是否包含恐怖内容")
        assert compliance.judgeHorrorImage(webdriverStaterGetImage)

    def testAnomalyImage(self, webdriverStaterGetImage):
        print("判断图片是否是AI错图")
        assert compliance.judgeAnomalyImage(webdriverStaterGetImage)

    def testAnalyzeHeadingsWithSelenium(self, webdriverStater):
        print("判断网页结构是否正常")
        assert compliance.analyze_headings_with_selenium(webdriverStater)

    def testMatchKeyword(self, webdriverStaterGetText, webdriverStaterGetKeyword):
        print("判断关键字密度")
        assert compliance.matchKeyword(webdriverStaterGetText, webdriverStaterGetKeyword)

    def testDuplicateBySearch(self, webdriverStaterGetText):
        print("判断文章是否伪原创")
        # assert antiCompliance.check_duplicate_by_search(webdriverStaterGetText)
        assert antiCompliance.is_plagiarized(webdriverStaterGetText)

    def testRedirectDeception(self, webdriverStater):
        print("判断重定向欺骗")
        assert antiCompliance.Redirect_deception(webdriverStater)
        webdriverStater.quit()

    def testLinkWithIpqs(self, webdriverStater):
        print("判断外链作弊")
        assert antiCompliance.analyze_links(webdriverStater)

    def testCheckCloaking(self, webdriverStater):
        print("判断cloaking欺骗")
        assert antiCompliance.check_cloaking(webdriverStater.current_url)

    def testAnalyzeKeywordStuffingWithDensity(self, webdriverStater):
        print("测试关键词堆叠")
        assert antiCompliance.analyze_keyword_stuffing_with_density(webdriverStater.current_url)


if __name__ == '__main__':
    pytest.main()