import csv
import io
import sys
import logging
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

from pages.aiTest import aiTest, antiCompliance, compliance
from selenium import webdriver
import allure
import subprocess
from bs4 import BeautifulSoup
import requests

# @pytest.fixture(scope="session", autouse=True)
# def generate_csv_data():
#     subprocess.run(["python", "/Users/edy/PycharmProjects/workProject/getYesterdayURL.py"])

# ---------------------------
# 工具函数：数据加载与校验
# ---------------------------
def load_urls_from_csv(csv_path='../utils/yesterdayURL.csv'):
# def load_urls_from_csv(csv_path='Utils/yesterdayURL.csv'):
    """从无表头的CSV读取URL"""
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)  # 不使用DictReader
        return [row[0] for row in reader if row]  # 提取每行第一个元素

def get_soup_from_url(url, timeout=10):
    """获取网页并返回 BeautifulSoup 对象"""
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup, ''
    except Exception as e:
        return None, str(e)

@pytest.fixture(scope="module", params=load_urls_from_csv())
def url(request):
    date_str, url_str = request.param
    soup, error = get_soup_from_url(url_str)
    allure.dynamic.parameter("Test Date", date_str)
    allure.dynamic.link(url_str)
    return {
        "date": date_str,
        "url": url_str,
        "soup": soup,
        "error": error
    }

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
    @allure.story("文章合规检测——测试图片")
    def testCheckImage(self, webdriverStater, url):
        print("测试图片")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert aiseoTest.checkImage(webdriverStater)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——测试文章和关键字的关系")
    def testCheckTextAndKeyword(self, webdriverStater, url):
        print('测试文章和关键字的关系')
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert aiseoTest.checkTextAndKeyword(webdriverStater)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——测试文章和图片的关系")
    def testCheckTextAndImage(self, webdriverStaterGetText, url,webdriverStaterGetImage):
        print('测试文章和图片的关系')
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert aiseoTest.checkTextAndImage(webdriverStaterGetText,webdriverStaterGetImage)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断文章是否包含违禁词")
    def testJudgeLllegalWords(self, webdriverStaterGetText, url):
        print("判断文章是否包含违禁词")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.JudgeLllegalWords(webdriverStaterGetText)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断图片状态码")
    def testImageCode(self, webdriverStaterGetImage, url):
        print("判断图片状态码")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.checkImage(webdriverStaterGetImage)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断图片是否包含黄色内容")
    def testjudgeNSFWImage(self, webdriverStaterGetImage, url):
        print("判断图片是否包含黄色内容")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.judgeNSFWImage(webdriverStaterGetImage)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断图片是否包含恐怖内容")
    def testHorrorImage(self, webdriverStaterGetImage, url):
        print("判断图片是否包含恐怖内容")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.judgeHorrorImage(webdriverStaterGetImage)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断图片是否是AI错图")
    def testAnomalyImage(self, webdriverStaterGetImage, url):
        print("判断图片是否是AI错图")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.judgeAnomalyImage(webdriverStaterGetImage)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__

    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断网页结构是否正常")
    def testAnalyzeHeadingsWithSelenium(self,url, webdriverStater,webdriverStaterGetText):
        print("判断网页结构是否正常")
        # 动态设置 feature 名称为当前 URL
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.analyze_headings_with_selenium(webdriverStater, webdriverStaterGetText)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章合规检测——判断关键字密度")
    def testMatchKeyword(self, webdriverStaterGetText, url, webdriverStaterGetKeyword):
        print("判断关键字密度")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert compliance.matchKeyword(webdriverStaterGetText, webdriverStaterGetKeyword)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章逆合规检测——判断文章是否伪原创")
    def testDuplicateBySearch(self, webdriverStaterGetText, url):
        print("判断文章是否伪原创")
        allure.dynamic.feature(url)
        # assert antiCompliance.check_duplicate_by_search(webdriverStaterGetText)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert antiCompliance.is_plagiarized(webdriverStaterGetText)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章逆合规检测——判断重定向欺骗")
    def testRedirectDeception(self, webdriverStater, url):
        print("判断重定向欺骗")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert antiCompliance.Redirect_deception(webdriverStater)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章逆合规检测——判断外链作弊")
    def testLinkWithIpqs(self, webdriverStater, url):
        print("判断外链作弊")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert antiCompliance.analyze_links(webdriverStater)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章逆合规检测——判断cloaking欺骗")
    def testCheckCloaking(self, webdriverStater, url):
        print("判断cloaking欺骗")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert antiCompliance.check_cloaking(webdriverStater.current_url)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__


    @allure.suite("AI SEO 合规检测")
    @allure.title("文本合规检查: {url}")
    @allure.story("文章逆合规检测——测试关键词堆叠")
    def testAnalyzeKeywordStuffingWithDensity(self, webdriverStater, url):
        print("测试关键词堆叠")
        allure.dynamic.feature(url)
        captured_output = io.StringIO()
        sys.stdout = captured_output  # 重定向print输出到captured_output
        try:
            assert antiCompliance.analyze_keyword_stuffing_with_density(webdriverStater.current_url)
        except AssertionError as e:
            # 捕获到失败
            sys.stdout = sys.__stdout__  # 恢复标准输出

            printed_logs = captured_output.getvalue()  # 获取之前所有print的内容
            error_message = f"断言失败: {str(e)}\n打印日志:\n{printed_logs}"
            print(error_message)  # 也可以只log
            logging.error(error_message)
            raise  # 最后记得继续抛出，让pytest知道是失败
        finally:
            sys.stdout = sys.__stdout__

if __name__ == '__main__':
    pytest.main()